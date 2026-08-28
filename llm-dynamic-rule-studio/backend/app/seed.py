from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models.field import FieldDefinition

SEED_FIELDS = [
    {
        "key": "cart_total",
        "label": "Cart Total",
        "data_type": "number",
        "operators": ["eq", "neq", "gt", "gte", "lt", "lte"],
    },
    {
        "key": "segment",
        "label": "Customer Segment",
        "data_type": "enum",
        "operators": ["eq", "neq", "in", "not_in"],
    },
    {
        "key": "loyalty_tier",
        "label": "Loyalty Tier",
        "data_type": "enum",
        "operators": ["eq", "neq", "in", "not_in"],
    },
    {
        "key": "order_count",
        "label": "Order Count",
        "data_type": "number",
        "operators": ["eq", "neq", "gt", "gte", "lt", "lte"],
    },
    {
        "key": "country",
        "label": "Country",
        "data_type": "string",
        "operators": ["eq", "neq", "contains", "in", "not_in"],
    },
    {
        "key": "is_vip",
        "label": "Is VIP",
        "data_type": "boolean",
        "operators": ["eq", "neq"],
    },
    {
        "key": "product_category",
        "label": "Product Category",
        "data_type": "string",
        "operators": ["eq", "neq", "contains", "in", "not_in"],
    },
]


async def seed_field_definitions() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(FieldDefinition.key))
        existing = set(result.scalars().all())
        created = False
        for item in SEED_FIELDS:
            if item["key"] in existing:
                continue
            session.add(FieldDefinition(**item))
            created = True
        if created:
            await session.commit()
