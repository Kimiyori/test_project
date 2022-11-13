from pydantic import BaseModel, Field


class UserData(BaseModel):
    """Validate user data during registeration"""

    username: str = Field(description="username", min_length=8, max_length=50)
    password: str = Field(description="password", min_length=8, max_length=36)
