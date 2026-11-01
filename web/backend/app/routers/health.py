from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends

from ..db import get_db
from ..schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)) -> HealthOut:
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "down"
    return HealthOut(status="ok" if database == "ok" else "degraded", database=database, version="1.0.0")
