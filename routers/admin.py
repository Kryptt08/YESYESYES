from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import hashlib
import secrets

from database import get_conn, dict_rows, dict_row
from schemas import PetCreate, PetUpdate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

_sessions: dict = {}

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256(b"bgsgg_admin").hexdigest()


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_session_user(request: Request):
    token = request.cookies.get("session")
    return _sessions.get(token)


def require_admin(request: Request):
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
        token = secrets.token_hex(32)
        _sessions[token] = username
        resp = RedirectResponse("/admin/", status_code=302)
        resp.set_cookie("session", token, httponly=True, samesite="lax")
        return resp
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid username or password"}
    )


@router.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("session")
    _sessions.pop(token, None)
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie("session")
    return resp


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(require_admin)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM pets
        ORDER BY
          CASE rarity
            WHEN 'Limited'   THEN 0
            WHEN 'Secret'    THEN 1
            WHEN 'Legendary' THEN 2
            ELSE 3
          END,
          CASE WHEN value ~ '^[0-9]+(\\.[0-9]+)?$' THEN CAST(value AS NUMERIC) ELSE 0 END DESC,
          name ASC
    """)
    pets = dict_rows(cur, cur.fetchall())
    cur.execute("SELECT * FROM value_history ORDER BY changed_at DESC LIMIT 10")
    recent = dict_rows(cur, cur.fetchall())
    cur.close()
    conn.close()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "pets": pets, "recent": recent, "user": user},
    )


@router.post("/pets/add")
async def add_pet(pet: PetCreate, user: str = Depends(require_admin)):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO pets (name, rarity, value, shiny_value, image_url, shiny_image_url, note, exists_normal, exists_shiny, demand, trend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (pet.name, pet.rarity, pet.value, pet.shiny_value, pet.image_url, pet.shiny_image_url, pet.note, pet.exists_normal, pet.exists_shiny, pet.demand, pet.trend),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Could not add pet: {e}")
    cur.close()
    conn.close()
    return {"success": True, "message": f"{pet.name} added"}


@router.patch("/pets/{pet_id}")
async def update_pet_value(
    pet_id: int,
    update: PetUpdate,
    user: str = Depends(require_admin),
):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM pets WHERE id = %s", (pet_id,))
    row = dict_row(cur, cur.fetchone())
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")

    cur.execute(
        """
        INSERT INTO value_history
            (pet_id, pet_name, old_value, new_value, old_shiny, new_shiny, changed_by, reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (pet_id, row["name"], row["value"], update.value,
         row["shiny_value"], update.shiny_value, user, update.reason),
    )

    cur.execute(
        """
        UPDATE pets
        SET value = %s, shiny_value = %s, image_url = %s, shiny_image_url = %s,
            note = %s, exists_normal = %s, exists_shiny = %s,
            demand = %s, trend = %s,
            updated_at = to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
        WHERE id = %s
        """,
        (update.value, update.shiny_value, update.image_url, update.shiny_image_url,
         update.note, update.exists_normal, update.exists_shiny,
         update.demand, update.trend, pet_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True, "message": f"Value updated for {row['name']}"}


@router.delete("/pets/{pet_id}")
async def delete_pet(pet_id: int, user: str = Depends(require_admin)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM pets WHERE id = %s", (pet_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")
    cur.execute("DELETE FROM pets WHERE id = %s", (pet_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True, "message": f"{row[0]} deleted"}
