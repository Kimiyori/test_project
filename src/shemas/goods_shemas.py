from pydantic import BaseModel, Field, root_validator


class CommodityCreate(BaseModel):
    """Validate create good"""

    name: str = Field(description="name", max_length=256)
    description: str = Field(description="description", max_length=500)
    price: int

    @root_validator
    @classmethod
    def validate_data(cls, values: dict[str, str | int]) -> dict[str, str | int]:
        if any(values[field] is None for field in values):
            raise ValueError("must provide all fields")
        return values


class CommodityUpdate(BaseModel):
    """Validate update good"""

    name: str | None = Field(description="name", max_length=256)
    description: str | None = Field(description="description", max_length=500)
    price: int | None

    @root_validator
    @classmethod
    def validate_data(cls, values: dict[str, str | int]) -> dict[str, str | int]:
        if all(values[field] is None for field in values):
            raise ValueError("must provide at least one field that needs to be changed")
        return values
