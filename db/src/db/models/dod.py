from pydantic import BaseModel


class DoDItem(BaseModel):
    description: str
    expected_outcome: str
    exec: str | None = None
