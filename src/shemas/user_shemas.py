from pydantic import BaseModel, Field, validator


class UserData(BaseModel):
    """Validate user data during registeration"""

    username: str = Field(description="username", min_length=8, max_length=50)
    password: str = Field(description="password", min_length=8, max_length=36)


class ChangeUserStatus(BaseModel):
    """validate data for changing user status"""

    id: int
    status: str

    @validator("status")
    @classmethod
    def status_validate(cls, value: str) -> str:
        if value not in ("disable", "enable"):
            raise ValueError("must be set either 'enable' or 'disable' in url")
        return value
