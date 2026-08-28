import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.rule import Rule
from app.schemas.rule import RuleCreate, RuleOut, RuleUpdate

router = APIRouter(prefix="/rules", tags=["rules"])


def _tree_to_dict(tree: Any) -> dict:
    if hasattr(tree, "model_dump"):
        return tree.model_dump()
    return tree


@router.get("", response_model=list[RuleOut])
async def list_rules(db: AsyncSession = Depends(get_db)) -> list[Rule]:
    result = await db.execute(select(Rule).order_by(Rule.updated_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
async def create_rule(payload: RuleCreate, db: AsyncSession = Depends(get_db)) -> Rule:
    rule = Rule(
        name=payload.name,
        description=payload.description,
        status=payload.status,
        condition_tree=_tree_to_dict(payload.condition_tree),
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=RuleOut)
async def get_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Rule:
    rule = await db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleOut)
async def update_rule(
    rule_id: uuid.UUID, payload: RuleUpdate, db: AsyncSession = Depends(get_db)
) -> Rule:
    rule = await db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    data = payload.model_dump(exclude_unset=True)
    if "condition_tree" in data and data["condition_tree"] is not None:
        data["condition_tree"] = _tree_to_dict(data["condition_tree"])

    for key, value in data.items():
        setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    rule = await db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
