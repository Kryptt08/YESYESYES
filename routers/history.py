from fastapi import APIRouter, Query
from typing import List
from database import get_conn, dict_rows
from schemas import HistoryOut

router = APIRouter()


@router.get("/", response_model=List[HistoryOut])
def get_history(limit: int = Query(default=50, le=200)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM value_history ORDER BY changed_at DESC LIMIT %s",
        (limit,),
    )
    rows = dict_rows(cur, cur.fetchall())
    cur.close()
    conn.close()
    return rows


@router.get("/{pet_id}", response_model=List[HistoryOut])
def get_pet_history(pet_id: int, limit: int = Query(default=20, le=100)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM value_history WHERE pet_id = %s ORDER BY changed_at DESC LIMIT %s",
        (pet_id, limit),
    )
    rows = dict_rows(cur, cur.fetchall())
    cur.close()
    conn.close()
    return rows
