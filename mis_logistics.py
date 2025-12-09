from datetime import date

# -----------------------------
# 1. Initial data: inventory and orders
# -----------------------------

inventory = {
    "Laptop": 10,
    "Headphones": 30,
    "Keyboard": 20,
}

orders = [
    {"order_id": 1, "product": "Laptop", "qty": 2, "customer": "Asha", "order_date": date(2025, 12, 1)},
    {"order_id": 2, "product": "Headphones", "qty": 5, "customer": "Rahul", "order_date": date(2025, 12, 1)},
    {"order_id": 3, "product": "Laptop", "qty": 4, "customer": "Meera", "order_date": date(2025, 12, 2)},
    {"order_id": 4, "product": "Keyboard", "qty": 3, "customer": "Vikram", "order_date": date(2025, 12, 2)},
    {"order_id": 5, "product": "Laptop", "qty": 6, "customer": "Kiran", "order_date": date(2025, 12, 3)},  # may not have full stock
]

# -----------------------------
# 2. Order processing: allocate stock
# -----------------------------

shipments = []

for order in orders:
    product = order["product"]
    qty_requested = order["qty"]
    stock_available = inventory.get(product, 0)

    if stock_available >= qty_requested:
        # full allocation
        inventory[product] -= qty_requested
        shipped_qty = qty_requested
        status = "Allocated"
        note = "Full quantity allocated"
    elif stock_available > 0:
        # partial allocation
        inventory[product] = 0
        shipped_qty = stock_available
        status = "Partially Allocated"
        note = f"Only {shipped_qty} out of {qty_requested} available"
    else:
        # no stock
        shipped_qty = 0
        status = "Backorder"
        note = "No stock available"

    shipments.append({
        "order_id": order["order_id"],
        "product": product,
        "customer": order["customer"],
        "order_date": order["order_date"],
        "requested_qty": qty_requested,
        "shipped_qty": shipped_qty,
        "allocation_status": status,
        "note": note,
    })

# -----------------------------
# 3. Delivery status update (tracking)
# -----------------------------

# In real life this comes from scanners / mobile app updates
delivery_updates = {
    1: {"delivery_status": "Delivered", "on_time": True},
    2: {"delivery_status": "Delivered", "on_time": True},
    3: {"delivery_status": "Delivered", "on_time": False},
    4: {"delivery_status": "In Transit", "on_time": False},
    5: {"delivery_status": "Not Shipped", "on_time": False},  # due to limited stock
}

for shipment in shipments:
    update = delivery_updates.get(shipment["order_id"], {})
    shipment["delivery_status"] = update.get("delivery_status", "Unknown")
    shipment["on_time"] = update.get("on_time", False)

# -----------------------------
# 4. Reverse logistics: returns
# -----------------------------

# Only delivered orders can have returns
returns = [
    {"order_id": 1, "product": "Laptop", "qty_returned": 1, "reason": "Defective", "condition": "Damaged"},
    {"order_id": 2, "product": "Headphones", "qty_returned": 2, "reason": "Not needed", "condition": "Good"},
]

# Process returns and update inventory
for r in returns:
    for shipment in shipments:
        if shipment["order_id"] == r["order_id"]:
            shipment.setdefault("qty_returned", 0)
            shipment["qty_returned"] += r["qty_returned"]

            # If condition is good, returned item goes back to inventory
            if r["condition"] == "Good":
                inventory[r["product"]] = inventory.get(r["product"], 0) + r["qty_returned"]
            break

# -----------------------------
# 5. MIS-style summary reports
# -----------------------------

total_orders = len(orders)
total_shipped = sum(1 for s in shipments if s["shipped_qty"] > 0)
total_backorders = sum(1 for s in shipments if s["allocation_status"] == "Backorder")
on_time_deliveries = sum(
    1 for s in shipments
    if s.get("delivery_status") == "Delivered" and s.get("on_time")
)
late_deliveries = sum(
    1 for s in shipments
    if s.get("delivery_status") == "Delivered" and not s.get("on_time")
)
total_returns = sum(s.get("qty_returned", 0) for s in shipments)

print("=== DAILY LOGISTICS MIS REPORT ===")
print(f"Total orders received: {total_orders}")
print(f"Orders with stock allocated (full or partial): {total_shipped}")
print(f"Orders on backorder (no stock): {total_backorders}")
print(f"On-time deliveries: {on_time_deliveries}")
print(f"Late deliveries: {late_deliveries}")
print(f"Total units returned (reverse logistics): {total_returns}")

print("\nRemaining inventory levels:")
for product, stock in inventory.items():
    print(f"  {product}: {stock} units")

print("\nShipment-level view:")
for s in shipments:
    print(
        f"Order {s['order_id']} | {s['product']} | Requested: {s['requested_qty']} | "
        f"Shipped: {s['shipped_qty']} | Status: {s['allocation_status']} | "
        f"Delivery: {s['delivery_status']} | Returned: {s.get('qty_returned', 0)}"
    )
