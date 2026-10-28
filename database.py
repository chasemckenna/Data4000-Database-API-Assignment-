"""Functions that talk to Supabase through its API.
Each .execute() sends a request to Supabase and .data holds the rows it sends back.
"""
from datetime import date
from supabase import create_client
from config import get_settings

client = None

# customers(name) and products(product_name) pull in the matching names
ORDER_COLUMNS = "*, customers(name), products(product_name)"


def get_client():
    # Create the Supabase client the first time, then reuse it
    global client
    if client is None:
        url, key = get_settings()
        client = create_client(url, key)
    return client


def get_customers():
    return get_client().table("customers").select("*").order("customer_id").execute().data


def get_products():
    return get_client().table("products").select("*").order("product_id").execute().data


def get_product(product_id):
    # Used right before saving so the order always gets the current price
    response = get_client().table("products").select("*").eq("product_id", product_id).execute()
    if response.data:
        return response.data[0]
    return None


def insert_order(customer_id, product_id, quantity, unit_price):
    # The database creates the order_id, so we don't send one
    new_order = {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": unit_price,
    }
    response = get_client().table("orders").insert(new_order).execute()
    return response.data


def get_order(order_id):
    response = (get_client().table("orders")
                .select(ORDER_COLUMNS)
                .eq("order_id", order_id)
                .execute())
    return response.data


def get_orders():
    # Newest orders first
    response = (get_client().table("orders")
                .select(ORDER_COLUMNS)
                .order("order_id", desc=True)
                .execute())
    return response.data
