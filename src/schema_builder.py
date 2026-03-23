from enum import StrEnum
from pydantic import BaseModel, create_model, Field


class AllowedTypes(StrEnum):
    string = "string"
    integer = "integer"
    float_ = "float"
    boolean = "boolean"
    list_string = "list[string]"


TYPE_MAPPING: dict[AllowedTypes, type] = {
    AllowedTypes.string: str,
    AllowedTypes.integer: int,
    AllowedTypes.float_: float,
    AllowedTypes.boolean: bool,
    AllowedTypes.list_string: list[str],
}

DEFAULT_VALUES: dict[AllowedTypes, object] = {
    AllowedTypes.string: "",
    AllowedTypes.integer: 0,
    AllowedTypes.float_: 0.0,
    AllowedTypes.boolean: False,
    AllowedTypes.list_string: [],
}


def build_item_model(
    schema_name: str,
    schema_definition: dict[str, dict],
) -> type[BaseModel]:
    """Create a dynamic Pydantic v2 model from a user-defined schema dict.

    Each entry in schema_definition is:
        field_name -> {"type": AllowedTypes value, "description": str}

    Returns a BaseModel subclass with those fields.
    """
    fields: dict = {}
    for field_name, field_info in schema_definition.items():
        field_type_key = AllowedTypes(field_info["type"])
        python_type = TYPE_MAPPING[field_type_key]
        default = DEFAULT_VALUES[field_type_key]
        description = field_info.get("description", "")
        # Use Optional-style defaults so OpenAI structured output doesn't force empty values
        fields[field_name] = (python_type, Field(default=default, description=description))

    return create_model(schema_name, **fields)


def build_result_model(item_model: type[BaseModel]) -> type[BaseModel]:
    """Wrap an item model in a container with a `items` list field.

    Neither OpenAI nor Anthropic accept list[Model] as response_format,
    so we wrap it: ResultModel(items=list[ItemModel]).
    """
    return create_model("ResultModel", items=(list[item_model], ...))
