import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.field import FieldDefinition
from app.schemas.field import FieldCreate, FieldOut

router = APIRouter(prefix="/fields", tags=["fields"])


@router.get("", response_model=list[FieldOut])
async def list_fields(db: AsyncSession = Depends(get_db)) -> list[FieldDefinition]:
    result = await db.execute(select(FieldDefinition).order_by(FieldDefinition.key))
    return list(result.scalars().all())


@router.post("", response_model=FieldOut, status_code=status.HTTP_201_CREATED)
async def create_field(
    payload: FieldCreate, db: AsyncSession = Depends(get_db)
) -> FieldDefinition:
    existing = await db.execute(
        select(FieldDefinition).where(FieldDefinition.key == payload.key)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Field key already exists")

    field = FieldDefinition(
        key=payload.key,
        label=payload.label,
        data_type=payload.data_type,
        operators=payload.operators,
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return field


@router.get("/{field_id}", response_model=FieldOut)
async def get_field(
    field_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> FieldDefinition:
    field = await db.get(FieldDefinition, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
