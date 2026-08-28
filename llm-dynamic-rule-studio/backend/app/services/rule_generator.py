from __future__ import annotations

import json
from typing import Any

from app.schemas.condition import GeneratedField, GeneratedRulePayload
from app.services.json_extract import extract_json_object
from app.services.ollama_client import OllamaClient

SYSTEM_PROMPT = """You are a business-rules expert. Convert natural language into a structured rule.

Keep reasoning brief. Your final answer MUST be ONLY valid JSON (no markdown) matching this EXACT shape:
{
  "name": "string",
  "description": "string",
  "fields": [
    {
      "key": "snake_case_key",
      "label": "Human Label",
      "data_type": "string|number|boolean|enum",
      "operators": ["eq","neq","gt","gte","lt","lte","contains","in","not_in"]
    }
  ],
  "condition_tree": {
    "type": "group",
    "logic": "AND",
    "children": [
      {
        "type": "condition",
        "field": "field_key",
        "operator": "eq",
        "value": "example"
      }
    ]
  }
}

CRITICAL:
- Use "logic" (AND/OR), never "operator", on groups.
- Use "children" array, never "conditions".
- Use operators exactly: eq,neq,gt,gte,lt,lte,contains,in,not_in (not =, >, <).
- fields must be objects with key/label/data_type/operators, not bare strings.
- Prefer catalog fields. Output JSON quickly with minimal reasoning.
"""

OPERATOR_MAP = {
    "=": "eq",
    "==": "eq",
    "equals": "eq",
    "!=": "neq",
    "<>": "neq",
    "not_equals": "neq",
    ">": "gt",
    "greater_than": "gt",
    ">=": "gte",
    "<": "lt",
    "less_than": "lt",
    "<=": "lte",
    "like": "contains",
}


class RuleGenerator:
    def __init__(self, ollama: OllamaClient) -> None:
        self.ollama = ollama

    async def generate(
        self,
        user_prompt: str,
        available_fields: list[dict[str, Any]],
    ) -> tuple[str, GeneratedRulePayload]:
        catalog = json.dumps(available_fields, indent=2)
        user_content = (
            f"Available field catalog:\n{catalog}\n\n"
            f"User request:\n{user_prompt}\n\n"
            "Return ONLY the JSON object with keys name, description, fields, condition_tree."
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        raw = await self.ollama.chat(messages)
        # Do not do a second full LLM round-trip — on CPU that doubles
        # multi-minute waits and causes proxy/browser disconnects.
        payload = self._parse(raw)
        return raw, payload

    def _parse(self, raw: str) -> GeneratedRulePayload:
        data = extract_json_object(raw)
        normalized = self._normalize_payload(data)
        return GeneratedRulePayload.model_validate(normalized)

    def _normalize_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        fields = self._normalize_fields(data.get("fields"), data.get("condition_tree"))
        tree = self._normalize_tree(data.get("condition_tree") or {})
        return {
            "name": data.get("name") or "Generated Rule",
            "description": data.get("description"),
            "fields": fields,
            "condition_tree": tree,
        }

    def _normalize_fields(
        self, fields: Any, tree: Any
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        if isinstance(fields, list):
            for item in fields:
                if isinstance(item, str):
                    normalized.append(
                        GeneratedField(
                            key=item,
                            label=item.replace("_", " ").title(),
                            data_type="string",
                            operators=["eq", "neq", "gt", "gte", "lt", "lte"],
                        ).model_dump()
                    )
                elif isinstance(item, dict) and item.get("key"):
                    normalized.append(
                        GeneratedField(
                            key=item["key"],
                            label=item.get("label")
                            or str(item["key"]).replace("_", " ").title(),
                            data_type=item.get("data_type") or "string",
                            operators=item.get("operators")
                            or ["eq", "neq", "gt", "gte", "lt", "lte"],
                        ).model_dump()
                    )

        # Ensure fields referenced in the tree exist.
        used = self._collect_field_keys(tree if isinstance(tree, dict) else {})
        existing = {f["key"] for f in normalized}
        for key in used:
            if key not in existing:
                normalized.append(
                    GeneratedField(
                        key=key,
                        label=key.replace("_", " ").title(),
                        data_type="string",
                        operators=["eq", "neq", "gt", "gte", "lt", "lte"],
                    ).model_dump()
                )
        return normalized

    def _collect_field_keys(self, node: dict[str, Any]) -> set[str]:
        keys: set[str] = set()
        if not isinstance(node, dict):
            return keys
        if node.get("field"):
            keys.add(str(node["field"]))
        for child in node.get("children") or node.get("conditions") or []:
            if isinstance(child, dict):
                keys |= self._collect_field_keys(child)
        return keys

    def _normalize_tree(self, node: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(node, dict):
            return {"type": "group", "logic": "AND", "children": []}

        # Leaf condition
        if "field" in node and (
            node.get("type") == "condition"
            or "operator" in node
            or "op" in node
            or "value" in node
        ) and "children" not in node and "conditions" not in node:
            op = str(node.get("operator") or node.get("op") or "eq").lower()
            op = OPERATOR_MAP.get(op, op)
            if op not in {
                "eq",
                "neq",
                "gt",
                "gte",
                "lt",
                "lte",
                "contains",
                "in",
                "not_in",
            }:
                op = "eq"
            return {
                "type": "condition",
                "field": str(node["field"]),
                "operator": op,
                "value": node.get("value"),
            }

        # Group
        logic = node.get("logic") or node.get("operator") or node.get("combinator") or "AND"
        logic = str(logic).upper()
        if logic not in {"AND", "OR"}:
            # Model sometimes puts comparison ops on groups; default AND.
            logic = "AND"
        children_raw = node.get("children") or node.get("conditions") or []
        children = [
            self._normalize_tree(child)
            for child in children_raw
            if isinstance(child, dict)
        ]
        return {"type": "group", "logic": logic, "children": children}
