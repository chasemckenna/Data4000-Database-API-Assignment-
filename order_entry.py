# DATA 4000 - Create and verify customer orders with Supabase
# Run with: python order_entry.py

from database import get_customers, get_products, insert_order, get_order


def show_customers(customers):
    print("\nCUSTOMERS")
    print(f"{'ID':<5}{'Name':<20}")
    print("-" * 25)
    for customer in customers:
        print(f"{customer['customer_id']:<5}{customer['name']:<20}")


def show_products(products):
    print("\nPRODUCTS")
    print(f"{'ID':<5}{'Product':<18}{'Price':>8}")
    print("-" * 31)
    for product in products:
        price = f"${float(product['price']):.2f}"
        print(f"{product['product_id']:<5}{product['product_name']:<18}{price:>8}")


def get_whole_number(prompt):
    # Keep asking until int() works, so "hello" or "1.5" doesn't crash the program
    while True:
        answer = input(prompt)
        try:
            return int(answer)
        except ValueError:
            print("Please enter a whole number like 3.")


def choose_customer(customers):
    while True:
        customer_id = get_whole_number("\nEnter a customer ID: ")
        for customer in customers:
            if customer["customer_id"] == customer_id:
                return customer
        print(f"There is no customer with ID {customer_id}. Pick one from the list.")


def choose_product(products):
    while True:
        product_id = get_whole_number("Enter a product ID: ")
        for product in products:
            if product["product_id"] == product_id:
                return product
        print(f"There is no product with ID {product_id}. Pick one from the list.")


def choose_quantity():
    while True:
        quantity = get_whole_number("Enter the quantity: ")
        if quantity > 0:
            return quantity
        print("Quantity has to be 1 or more.")


def ask_yes_or_no(prompt):
    while True:
        answer = input(prompt).strip().upper()
        if answer == "Y":
            return True
        if answer == "N":
            return False
        print("Please type Y or N.")


def show_summary(customer, product, quantity):
    price = float(product["price"])
    print("\nORDER SUMMARY")
    print(f"Customer:   {customer['name']}")
    print(f"Product:    {product['product_name']}")
    print(f"Quantity:   {quantity}")
    print(f"Unit price: ${price:.2f}")
    print(f"Total:      ${price * quantity:.2f}")


def save_order(customer, product, quantity):
    # Returns the new order_id, or None if the save didn't work
    try:
        rows = insert_order(customer["customer_id"], product["product_id"],
                            quantity, product["price"])
    except Exception:
        # Don't print the error itself in case it has connection details in it
        print("Sorry, the order could not be saved. Check your connection and .env file.")
        return None

    if not rows:
        print("Supabase did not confirm the order, so it was not saved.")
        return None

    order_id = rows[0]["order_id"]
    print(f"\nOrder saved! The new order ID is {order_id}.")
    return order_id


def verify_order(order_id):
    # Ask the database for the order again to prove it was really saved
    try:
        rows = get_order(order_id)
    except Exception:
        rows = []

    if not rows:
        print(f"Could not verify order {order_id}. Check the orders table in Supabase.")
        return

    order = rows[0]
    price = float(order["unit_price"])
    total = price * order["quantity"]

    print("\nSAVED ORDER (from Supabase)")
    print(f"{'Order ID':<10}{'Customer':<16}{'Product':<16}{'Qty':<5}"
          f"{'Unit Price':>11}{'Total':>10}  {'Order Date'}")
    print("-" * 80)
    print(f"{order['order_id']:<10}{order['customers']['name']:<16}"
          f"{order['products']['product_name']:<16}{order['quantity']:<5}"
          f"{'$' + format(price, '.2f'):>11}{'$' + format(total, '.2f'):>10}  {order['order_date']}")


def place_one_order():
    # Load fresh data each time so a new order never uses old information
    customers = get_customers()
    products = get_products()
    show_customers(customers)
    show_products(products)

    customer = choose_customer(customers)
    product = choose_product(products)
    quantity = choose_quantity()

    show_summary(customer, product, quantity)
    if not ask_yes_or_no("\nConfirm this order? (Y/N): "):
        print("Order cancelled. Nothing was saved.")
        return

    order_id = save_order(customer, product, quantity)
    if order_id is not None:
        verify_order(order_id)


def main():
    print("Welcome to the Campus Store order entry program!")
    while True:
        try:
            place_one_order()
        except Exception:
            print("Could not load customers and products from Supabase. "
                  "Check your connection and .env file.")
            break

        if not ask_yes_or_no("\nWould you like to enter another order? (Y/N): "):
            print("Goodbye!")
            break


main()
