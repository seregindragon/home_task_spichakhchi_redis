from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Annotated

Currency = Annotated[Decimal, Field(max_digits=10, decimal_places=2, ge=0)]


# --- Product ---
class ProductCreate(BaseModel):
    name: str
    price: Currency


class ProductResponse(BaseModel):
    id: int
    name: Annotated[str, Field(examples=["Shirt"])]
    price: Currency
    model_config = {"from_attributes": True}


# --- Customer ---
class CustomerCreate(BaseModel):
    name: str
    email: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}


# --- Order ---
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    model_config = {"from_attributes": True}


class OrderItemDetailResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse
    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    stripe_payment_intent_id: str
    items: list[OrderItemResponse]
    model_config = {"from_attributes": True}


class OrderDetailResponse(BaseModel):
    id: int
    customer_id: int
    stripe_payment_intent_id: str
    items: list[OrderItemDetailResponse]
    model_config = {"from_attributes": True}


class CartItem(BaseModel):
    model_config = {"from_attributes": True}
    product_id: int
    quantity: int
    price: Currency


class Cart(BaseModel):
    cart_items: list[CartItem]
    total_price: Currency
