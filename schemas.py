from pydantic import BaseModel
from typing import Optional


class PetOut(BaseModel):
    id: int
    name: str
    rarity: str
    value: str
    shiny_value: Optional[str]
    image_url: Optional[str]
    shiny_image_url: Optional[str]
    note: Optional[str]
    exists_normal: Optional[str]
    exists_shiny: Optional[str]
    demand: Optional[int]
    trend: Optional[str]
    description: Optional[str]
    updated_at: str


class PetCreate(BaseModel):
    name: str
    rarity: str
    value: str = "0"
    shiny_value: Optional[str] = None
    image_url: Optional[str] = None
    shiny_image_url: Optional[str] = None
    note: Optional[str] = None
    exists_normal: Optional[str] = 0
    exists_shiny: Optional[str] = 0
    demand: Optional[int] = 0
    trend: Optional[str] = "stable"
    description: Optional[str] = None


class PetUpdate(BaseModel):
    value: str
    shiny_value: Optional[str] = None
    image_url: Optional[str] = None
    shiny_image_url: Optional[str] = None
    note: Optional[str] = None
    reason: Optional[str] = None
    exists_normal: Optional[str] = 0
    exists_shiny: Optional[str] = 0
    demand: Optional[int] = 0
    trend: Optional[str] = "stable"
    description: Optional[str] = None


class HistoryOut(BaseModel):
    id: int
    pet_id: int
    pet_name: str
    old_value: str
    new_value: str
    old_shiny: Optional[str]
    new_shiny: Optional[str]
    changed_by: str
    reason: Optional[str]
    changed_at: str
