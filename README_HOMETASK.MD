# Home Task — Async Shop Endpoint

## Task

Implement an async shop endpoint with a DB query. All I/O operations must be async.

## Implementation

### New endpoint: `GET /api/v1/orders/{order_id}`

Returns a single order with full product details for the authenticated customer.

**Auth:** Bearer token required. Returns 404 if order belongs to another customer.

**Response example:**
```json
{
  "id": 1,
  "customer_id": 3,
  "stripe_payment_intent_id": "pi_xxx",
  "items": [
    {
      "id": 1,
      "product_id": 2,
      "quantity": 3,
      "product": {
        "id": 2,
        "name": "Shirt",
        "price": "22.99"
      }
    }
  ]
}
```

### Files changed

| File | Change |
|------|--------|
| `shop/schemas.py` | Added `OrderItemDetailResponse`, `OrderDetailResponse` |
| `shop/routes/order.py` | Added `GET /{order_id}` endpoint |

### Why it satisfies the task

- All I/O async: `await db.execute(...)`, auth dependency is async
- Single SQL query via `joinedload(Order.items).joinedload(OrderItem.product)` — no N+1
- 404 on missing or unauthorized order
- Route order fixed: static `/check_payment` registered before parameterized `/{order_id}`