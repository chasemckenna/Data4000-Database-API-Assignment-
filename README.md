# Customer Order Entry - DATA 4000

This is a Python program that runs in the terminal. It lets you create an order for
a customer in the Campus Store Supabase database, then checks the database to make
sure the order was saved.

## Files
- `order_entry.py` - the main program
- `database.py` - functions that read from and write to Supabase
- `config.py` - loads the Supabase URL and secret key from `.env`
- `requirements.txt` - packages to install
- `.env.example` - template for your `.env` file (placeholders only)

## Setup
You need the Supabase project from class with the `customers`, `products`, and
`orders` tables already loaded.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and put in your own project URL and `sb_secret_` key.
`.env` is in `.gitignore`, so it doesn't get uploaded to GitHub.

## Running it
```bash
python order_entry.py
```

## How it works
1. It gets the customers and products from Supabase and prints them in tables.
2. It asks for a customer ID, a product ID, and a quantity. `get_whole_number()` uses
   `try/except` so typing text or a decimal shows a message instead of crashing.
   The IDs are checked against the lists that came from the database, and the
   quantity has to be 1 or more.
3. It shows an order summary and asks Y or N. N cancels without saving anything.
   Y sends the order to Supabase. The price comes from the database, not from the
   user, and Supabase creates the order ID.
4. After saving, it uses the new order ID to query the database again and prints the
   saved order. The total is calculated from the `unit_price` stored in the database.
5. Extra credit: it asks if you want to enter another order and keeps going until you
   say N. It reloads the customers and products each time, so nothing carries over
   from the last order.

## Testing
I counted the rows in the orders table before and after the test run. It went from
62 to 63. The cancelled order didn't add anything, and the confirmed order added
exactly one.

| Test | What I typed | What happened |
|---|---|---|
| Text for customer ID | `hello` | Message, asked again |
| Customer ID that doesn't exist | `999` | Rejected, asked again |
| Product ID that doesn't exist | `0` | Rejected, asked again |
| Bad quantities | `0`, `-2`, `1.5`, `hello` | Each one rejected, asked again |
| Cancel at confirmation | `n` | "Order cancelled", nothing saved |
| Confirm a valid order | `y` | Order 1002 saved (one new row) |
| Check the new order | automatic | Order 1002 showed up in the saved order table |
| Wrong secret key | bad key in `.env` | Error message, no crash, key not shown |

### Terminal output
The customer and product lists printed again before the second order. I cut them
out below to keep this shorter.
```text
Welcome to the Campus Store order entry program!

CUSTOMERS
ID   Name                
-------------------------
1    Avery Morgan        
2    Jordan Patel        
3    Taylor Chen         
4    Casey Rivera        
5    Riley Brooks        
6    Morgan Lee          
7    Jamie Wilson        
8    Alex Kim            
9    Cameron Davis       
10   Quinn Garcia        
11   Sam Parker          
12   Drew Johnson        
13   Skyler Reed         
14   Reese Martin        
15   Rowan Lewis         
16   Peyton Clark        
17   Finley Hall         
18   Emerson Young       
19   Dakota Allen        
20   Harper Scott        

PRODUCTS
ID   Product              Price
-------------------------------
1    Notebook             $4.50
2    Pen Set              $6.00
3    Backpack            $45.00
4    Water Bottle        $18.00
5    Hoodie              $39.00
6    T-Shirt             $19.00
7    USB Drive           $12.50
8    Wireless Mouse      $24.00
9    Desk Lamp           $29.00
10   Coffee Mug          $10.00
11   Planner             $15.00
12   Laptop Stand        $35.00

Enter a customer ID: hello
Please enter a whole number like 3.

Enter a customer ID: 999
There is no customer with ID 999. Pick one from the list.

Enter a customer ID: 5
Enter a product ID: abc
Please enter a whole number like 3.
Enter a product ID: 0
There is no product with ID 0. Pick one from the list.
Enter a product ID: 7
Enter the quantity: 0
Quantity has to be 1 or more.
Enter the quantity: -2
Quantity has to be 1 or more.
Enter the quantity: 1.5
Please enter a whole number like 3.
Enter the quantity: hello
Please enter a whole number like 3.
Enter the quantity: 2

ORDER SUMMARY
Customer:   Riley Brooks
Product:    USB Drive
Quantity:   2
Unit price: $12.50
Total:      $25.00

Confirm this order? (Y/N): maybe
Please type Y or N.

Confirm this order? (Y/N): n
Order cancelled. Nothing was saved.

Would you like to enter another order? (Y/N): y

(customer and product lists printed again)
Enter a customer ID: 8
Enter a product ID: 5
Enter the quantity: 1

ORDER SUMMARY
Customer:   Alex Kim
Product:    Hoodie
Quantity:   1
Unit price: $39.00
Total:      $39.00

Confirm this order? (Y/N): y

Order saved! The new order ID is 1002.

SAVED ORDER (from Supabase)
Order ID  Customer        Product         Qty   Unit Price     Total  Order Date
--------------------------------------------------------------------------------
1002      Alex Kim        Hoodie          1         $39.00    $39.00  2026-10-21

Would you like to enter another order? (Y/N): N
Goodbye!
```

## References
Everything here is from class (the Supabase Python client, `input()`, `try/except`,
and f-strings). Docs I looked at:
- https://supabase.com/docs/reference/python/select
- https://supabase.com/docs/reference/python/insert
