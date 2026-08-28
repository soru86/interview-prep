from typing import Any, Literal

from pydantic import BaseModel, Field


LogicOp = Literal["AND", "OR"]
NodeType = Literal["condition", "group"]
Operator = Literal[
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    "contains",
    "in",
    "not_in",
]


class ConditionNode(BaseModel):
    type: Literal["condition"] = "condition"
    field: str
    operator: Operator
    value: Any


class GroupNode(BaseModel):
    type: Literal["group"] = "group"
    logic: LogicOp = "AND"
    children: list["ConditionNode | GroupNode"] = Field(default_factory=list)


ConditionTree = GroupNode
GroupNode.model_rebuild()


class GeneratedField(BaseModel):
    key: str
    label: str
    data_type: str
    operators: list[str] = Field(default_factory=list)


class GeneratedRulePayload(BaseModel):
    name: str
    description: str | None = None
    fields: list[GeneratedField] = Field(default_factory=list)
    condition_tree: ConditionTree
