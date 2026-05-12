import os

from dotenv import load_dotenv
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from stripe import StripeClient

from db import get_db, get_cart_items
from models import Customer, Order, OrderItem, Product
from schemas import OrderItemResponse, OrderResponse, OrderDetailResponse
from .security import get_current_user

load_dotenv()
stripe_client = StripeClient(os.environ["STRIPE_SECRET"])
router = APIRouter()


@router.post("/")
async def checkout(
    customer: Customer = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Create Order with the confirmed payment intent
    # 2. Create OrderItem based on CartItem
    # 3. Remove CartItem that belong to the current customer
    cart_items = await get_cart_items(customer.id, db)
    total_price = sum(item.subtotal for item in cart_items)
    intent = await stripe_client.v1.payment_intents.create_async(
        params={
            "amount": int(total_price * 100),
            "currency": "usd",
            "payment_method_types": ["card"],
        }
    )
    # 1. Create Order with the confirmed payment intent
    order = Order(
        customer_id=customer.id,
        stripe_payment_inten_id=intent.id,
    )
    db.add(order)
    await db.flush()  # Get the order.id for OrderItem creation

    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
        )
        db.add(order_item)

    for cart_item in cart_items:
        await db.delete(cart_item)
    await db.commit()

    confirmed_intent = await stripe_client.v1.payment_intents.confirm_async(
        intent.id, params={"payment_method": "pm_card_visa"}
    )
    return confirmed_intent.id


@router.get("/", response_model=list[OrderResponse])
async def get_oders(
    customer: Customer = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Order)
        .where(Order.customer_id == customer.id)
        .options(joinedload(Order.items))
    )
    result = await db.execute(stmt)
    responses = []
    for order in result.unique().scalars():
        items = [OrderItemResponse.model_validate(item) for item in order.items]
        resp = OrderResponse(
            id=order.id,
            items=items,
            customer_id=order.customer_id,
            stripe_payment_intent_id=order.stripe_payment_inten_id,
        )
        responses.append(resp)
    return responses


@router.get("/check_payment")
async def check_payment_id(intent_id: str):
    intent = await stripe_client.v1.payment_intents.retrieve_async(intent_id)
    print(intent.status)


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: int,
    customer: Customer = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.customer_id == customer.id)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
    )
    result = await db.execute(stmt)
    order = result.unique().scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
