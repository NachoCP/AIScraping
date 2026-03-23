"""Unified LLM extraction via LiteLLM — supports all providers and models."""

import json
import logging

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

from src.config import MAX_RETRIES

logger = logging.getLogger("aiscraping")

SYSTEM_PROMPT = (
    "You are an expert web scraper. Extract all objects matching the schema "
    "from the provided page content. Always prefer full, untruncated values — "
    "if a title or text appears truncated with '...' but a full version is "
    "available elsewhere in the content (e.g. in a link title or alt text), "
    "use the full version. If a value cannot be determined, use the default "
    "value for that type (empty string, 0, false, or empty list). "
    "Extract every matching object you find — return them all in the items list."
)


@retry(
    wait=wait_random_exponential(min=1, max=30),
    stop=stop_after_attempt(MAX_RETRIES),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract(
    markdown: str,
    result_model: type[BaseModel],
    litellm_model: str,
    api_key: str,
) -> BaseModel:
    """Extract structured data from markdown using any LLM via LiteLLM.

    Args:
        markdown: Page content as markdown.
        result_model: Pydantic model with an `items` list field.
        litellm_model: LiteLLM provider string, e.g. "openai/gpt-4.1-mini".
        api_key: API key for the provider.

    Returns:
        A Pydantic model instance with an `items` list.
    """
    import litellm

    logger.info("Extracting with %s", litellm_model)

    schema = result_model.model_json_schema()

    response = litellm.completion(
        model=litellm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": markdown},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "extraction_result",
                "strict": True,
                "schema": _make_strict_schema(schema),
            },
        },
        temperature=0,
        api_key=api_key,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)
    return result_model.model_validate(data)


def _make_strict_schema(schema: dict) -> dict:
    """Transform a Pydantic JSON schema into OpenAI strict-mode compatible schema.

    Recursively adds additionalProperties: false and makes all properties required.
    """
    schema = {k: v for k, v in schema.items() if k != "$defs"} if "$defs" not in schema else dict(schema)

    # Inline $defs references
    defs = schema.pop("$defs", {})
    schema = _resolve_refs(schema, defs)

    return _make_strict_object(schema)


def _resolve_refs(obj, defs: dict):
    """Recursively resolve $ref references."""
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_name = obj["$ref"].split("/")[-1]
            resolved = defs.get(ref_name, {})
            return _resolve_refs(resolved, defs)
        return {k: _resolve_refs(v, defs) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_refs(item, defs) for item in obj]
    return obj


def _make_strict_object(schema: dict) -> dict:
    """Add additionalProperties: false and required to all objects."""
    if isinstance(schema, dict):
        if schema.get("type") == "object" and "properties" in schema:
            schema["additionalProperties"] = False
            schema["required"] = list(schema["properties"].keys())
            for prop in schema["properties"].values():
                _make_strict_object(prop)
        if schema.get("type") == "array" and "items" in schema:
            _make_strict_object(schema["items"])
        for key in ("anyOf", "oneOf", "allOf"):
            if key in schema:
                for item in schema[key]:
                    _make_strict_object(item)
    return schema
