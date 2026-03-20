from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db, seed_db, cleanup_db
from routers import pets, admin, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(
    title="BGS.GG API",
    description="Backend for OG Bubble Gum Simulator Value List",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")

app.include_router(pets.router,    prefix="/api/pets",    tags=["Pets"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(admin.router,   prefix="/admin",       tags=["Admin"])


@app.get("/")
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pets")
async def serve_pets(request: Request):
    return templates.TemplateResponse("pets.html", {"request": request})

@app.get("/pet/{pet_id}")
async def serve_pet_detail(request: Request, pet_id: int):
    return templates.TemplateResponse("pet_detail.html", {"request": request, "pet_id": pet_id})
