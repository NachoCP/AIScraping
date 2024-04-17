from pydantic import BaseModel, create_model, Field
from enum import StrEnum


class AllowedTypes(StrEnum):
    string = "string"
    integer = "integer",
    float = "float"

type_mapping = {
    AllowedTypes.string: str,
    AllowedTypes.integer: int,
    AllowedTypes.float: float
}

# Dynamically create the Pydantic model from the schema
def create_pydantic_model_from_schema(schema_name, schema_definition):
    fields = {
        field_name: (type_mapping[field_info["type"]], Field(default=..., description=field_info.get("description")))
        for field_name, field_info in schema_definition.items()
    }
    return create_model(schema_name, **fields)


def model_to_dict(obj):
    if isinstance(obj, list):
        return [item.dict() for item in obj]
    else:
        return obj.dict()