from pydantic import BaseModel, root_validator
from Crypto.Hash import SHA1
from src.config import SECRET


class WebHook(BaseModel):
    """Validate data for webhook"""

    signature: str
    transaction_id: str
    user_id: int
    account_id: str
    amount: int

    @root_validator
    @classmethod
    def signature_validate(cls, values: dict[str, str | int]) -> dict[str, str | int]:
        def create_signature(values: dict[str, str | int]) -> str:
            code = (
                f"{SECRET}:"
                f"{values['transaction_id']}:"
                f"{values['user_id']}:"
                f"{values['account_id']}:"
                f"{values['amount']}"
            )
            guessed_signature = SHA1.new()
            guessed_signature.update(code.encode())
            return guessed_signature.hexdigest()

        guessed_signature = create_signature(values)
        if guessed_signature != values["signature"]:
            raise ValueError("Invalid signature")
        return values
