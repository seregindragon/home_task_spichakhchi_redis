from fastapi import Depends, APIRouter
from pydantic import TypeAdapter
from redis.asyncio import Redis

from models import Customer
from schemas import CartItem as CartItemSchema
from .security import get_current_user

router = APIRouter()
r = Redis(host="localhost", port=6379, decode_responses=True)
REDIS_CART_PREFIX = "shop:cart:items"
REDIS_CART_MODIF_PREFIX = "shop:cart:timestamp"
adapter = TypeAdapter(list[CartItemSchema])


@router.post("/")
async def sync_cart(
    cart_items: list[CartItemSchema],
    customer: Customer = Depends(get_current_user),
):
    key = REDIS_CART_PREFIX + str(customer.id)
    # 1. if client timestamp > server timestamp => delete server cart && store client cart
    # 2. else send expired error
    val = adapter.dump_json(cart_items).decode("utf-8")
    await r.set(key, val)


@router.get("/", response_model=list[CartItemSchema])
async def show_cart(
    customer: Customer = Depends(get_current_user),
):
    key = REDIS_CART_PREFIX + str(customer.id)
    items_json = await r.get(key)
    return adapter.validate_json(items_json)


@router.get("/delete_key")
async def delete_cart(
    customer: Customer = Depends(get_current_user),
):
    key = REDIS_CART_PREFIX + str(customer.id)
    await r.delete(key)
