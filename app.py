# DATA 4000 - Campus Store order entry web app
# Run locally with: streamlit run app.py

import hmac

import pandas as pd
import streamlit as st

from config import get_app_password
from database import (get_customers, get_products, get_product, insert_order,
                      get_order, get_orders)

st.set_page_config(page_title="Campus Store Order Entry", page_icon="🛒", layout="wide")

MONEY = st.column_config.NumberColumn(format="$%.2f")
ORDER_TABLE_COLUMNS = ["Order ID", "Customer", "Product", "Quantity",
                       "Unit Price", "Total", "Order Date"]


def check_password():
    # Runs before anything touches the database. The password lives in secrets, not in the code.
    if st.session_state.get("authenticated"):
        return True

    app_password = get_app_password()
    if not app_password:
        st.error("This app is locked because no APP_PASSWORD has been set in its secrets.")
        return False

    with st.form("login"):
        entered = st.text_input("App password", type="password")
        if st.form_submit_button("Log in"):
            if hmac.compare_digest(entered.encode(), app_password.encode()):
                st.session_state.authenticated = True
                st.rerun()
            st.error("That password is not correct.")
    return False


def load_data():
    # Every call goes to Supabase, so this always gets the current records
    st.session_state.customers = get_customers()
    st.session_state.products = get_products()
    st.session_state.orders = get_orders()


def orders_table(orders):
    # The total is calculated from the unit_price stored with each order
    rows = []
    for order in orders:
        unit_price = float(order["unit_price"])
        rows.append({
            "Order ID": order["order_id"],
            "Customer": (order.get("customers") or {}).get("name", "Unknown"),
            "Product": (order.get("products") or {}).get("product_name", "Unknown"),
            "Quantity": order["quantity"],
            "Unit Price": unit_price,
            "Total": unit_price * order["quantity"],
            "Order Date": order["order_date"],
        })
    return pd.DataFrame(rows, columns=ORDER_TABLE_COLUMNS)


def show_orders(orders):
    st.dataframe(orders_table(orders), hide_index=True,
                 column_config={"Unit Price": MONEY, "Total": MONEY})


def submit_order(customer, product, quantity, reviewed_price, confirmed):
    # This only runs when the Submit button is clicked, so reruns never insert an order
    if not confirmed:
        st.warning("Check the confirmation box before submitting. Nothing was saved.")
        return
    if not isinstance(quantity, int) or quantity < 1:
        st.error("Quantity has to be a whole number of 1 or more. Nothing was saved.")
        return

    # Get the price again right before saving in case it changed since the review
    try:
        current = get_product(product["product_id"])
    except Exception:
        st.error("Could not reach Supabase to check the current price. Nothing was saved.")
        return
    if current is None:
        st.error("That product is no longer in the database. Click Refresh Data. Nothing was saved.")
        return

    current_price = float(current["price"])
    if round(current_price, 2) != round(reviewed_price, 2):
        # Show the new price. The confirmation box resets because its key includes the price.
        for item in st.session_state.products:
            if item["product_id"] == product["product_id"]:
                item["price"] = current["price"]
        st.session_state.notice = (
            f"The price of {product['product_name']} changed from ${reviewed_price:.2f} "
            f"to ${current_price:.2f}. Review the new total and confirm again. Nothing was saved."
        )
        st.rerun()

    try:
        rows = insert_order(customer["customer_id"], product["product_id"], quantity, current_price)
    except Exception:
        # Don't show the error text in case it has connection details in it
        st.error("The order could not be saved. Check the connection to Supabase and try again.")
        return
    if not rows:
        st.error("Supabase did not confirm the order, so it was not saved.")
        return

    order_id = rows[0]["order_id"]

    # Ask the database for the order again to prove it was really saved
    try:
        saved = get_order(order_id)
    except Exception:
        saved = []

    st.session_state.last_order = {"order_id": order_id, "record": saved[0] if saved else None}
    st.session_state.form_number += 1  # new widget keys clear the form for the next order

    try:
        st.session_state.orders = get_orders()
    except Exception:
        st.session_state.notice = "The order history could not be updated. Click Refresh Data."
    st.rerun()


# ---------------- Page ----------------

st.title("🛒 Campus Store Order Entry")
st.write("Look up customers and products in the Campus Store Supabase database, "
         "enter a new order, and check that it was saved.")

if not check_password():
    st.stop()

if "form_number" not in st.session_state:
    st.session_state.form_number = 0

refresh_clicked = st.button("🔄 Refresh Data")
if refresh_clicked or "customers" not in st.session_state:
    try:
        load_data()
        if refresh_clicked:
            st.toast("Data refreshed from Supabase.")
    except Exception:
        st.error("Could not load data from Supabase. Check the connection settings and try again.")
        st.stop()

customers = st.session_state.customers
products = st.session_state.products
customers_by_id = {c["customer_id"]: c for c in customers}
products_by_id = {p["product_id"]: p for p in products}

# 1. Customers and products
left, right = st.columns(2)
with left:
    st.subheader("Customers")
    st.dataframe(pd.DataFrame(customers)[["customer_id", "name"]], hide_index=True,
                 column_config={"customer_id": "Customer ID", "name": "Name"})
with right:
    st.subheader("Products")
    st.dataframe(pd.DataFrame(products)[["product_id", "product_name", "category", "price"]],
                 hide_index=True,
                 column_config={"product_id": "Product ID", "product_name": "Product",
                                "category": "Category",
                                "price": st.column_config.NumberColumn("Price", format="$%.2f")})

# 2. Order entry
st.divider()
st.header("New Order")

if "notice" in st.session_state:
    st.warning(st.session_state.pop("notice"))

n = st.session_state.form_number
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    customer_id = st.selectbox(
        "Customer", options=list(customers_by_id), index=None, placeholder="Choose a customer",
        format_func=lambda cid: f"{customers_by_id[cid]['name']} (ID {cid})", key=f"customer_{n}")
with col2:
    product_id = st.selectbox(
        "Product", options=list(products_by_id), index=None, placeholder="Choose a product",
        format_func=lambda pid: f"{products_by_id[pid]['product_name']} (${float(products_by_id[pid]['price']):.2f})",
        key=f"product_{n}")
with col3:
    quantity = st.number_input("Quantity", min_value=1, step=1, value=1, key=f"quantity_{n}")

if customer_id is None or product_id is None:
    st.info("Choose a customer and a product to review the order.")
else:
    customer = customers_by_id[customer_id]
    product = products_by_id[product_id]
    price = float(product["price"])

    st.subheader("Review Order")
    st.dataframe(pd.DataFrame([{
        "Customer": customer["name"],
        "Product": product["product_name"],
        "Quantity": quantity,
        "Unit Price": price,
        "Total": price * quantity,
    }]), hide_index=True, column_config={"Unit Price": MONEY, "Total": MONEY})

    # Changing anything in the order (or the price) makes a new checkbox, so it starts unchecked
    confirmed = st.checkbox("I reviewed this order and want to save it.",
                            key=f"confirm_{n}_{customer_id}_{product_id}_{quantity}_{price}")
    if st.button("Submit Order", type="primary"):
        submit_order(customer, product, quantity, price, confirmed)

# 3. Result of the last saved order
if "last_order" in st.session_state:
    last = st.session_state.last_order
    st.success(f"Order {last['order_id']} was saved.")
    st.subheader("Saved Order (retrieved from Supabase)")
    if last["record"]:
        show_orders([last["record"]])
    else:
        st.warning(f"Order {last['order_id']} was saved, but it could not be retrieved for "
                   "verification. Do not submit it again. Click Refresh Data to look for it "
                   "in the order history.")

# 4. Order history
st.divider()
st.header("Order History")
history_customer = st.selectbox(
    "Show orders for", options=[None] + list(customers_by_id),
    format_func=lambda cid: "All customers" if cid is None else customers_by_id[cid]["name"])

history = st.session_state.orders
if history_customer is not None:
    history = [o for o in history if o["customer_id"] == history_customer]

total_value = sum(float(o["unit_price"]) * o["quantity"] for o in history)
m1, m2 = st.columns(2)
m1.metric("Orders", len(history))
m2.metric("Total value", f"${total_value:,.2f}")
show_orders(history)
