from fastapi import APIRouter, HTTPException
from typing import Optional, List
from database import get_conn, dict_rows, dict_row
from schemas import PetOut

router = APIRouter()


@router.get("/", response_model=List[PetOut])
def get_all_pets(
    rarity: Optional[str] = None,
    sort: Optional[str] = "value_desc",
):
    conn = get_conn()
    cur = conn.cursor()

    if rarity:
        cur.execute("SELECT * FROM pets WHERE rarity = %s", (rarity,))
    else:
        cur.execute("SELECT * FROM pets")

    rows = dict_rows(cur, cur.fetchall())
    cur.close()
    conn.close()

    order_map = {
        "value_desc": lambda p: (-float(p["value"]) if str(p["value"]).replace('.','',1).isdigit() else 0),
        "value_asc":  lambda p: (float(p["value"]) if str(p["value"]).replace('.','',1).isdigit() else 0),
        "name_asc":   lambda p: p["name"],
        "name_desc":  lambda p: p["name"],
    }
    reverse = sort == "name_desc"
    key = order_map.get(sort, order_map["value_desc"])
    rows.sort(key=key, reverse=(sort == "name_desc"))

    return rows


@router.get("/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pets WHERE id = %s", (pet_id,))
    row = dict_row(cur, cur.fetchone())
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Pet not found")
    return row
