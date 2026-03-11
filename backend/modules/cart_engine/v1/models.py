"""Cart Engine Models"""
from pydantic import BaseModel, Field, ConfigDict
import uuid

class CartItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    quantity: int = 1
    session_id: str

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = 1
    session_id: str

class CartItemUpdate(BaseModel):
    quantity: int
