# Campus Store Order Entry - DATA 4000

A Streamlit web app connected to the Campus Store Supabase database. You can look up
customers and products, enter an order, and check that it was saved. This replaces my
earlier terminal program (`order_entry.py`, still in the repo).

**Live app:** https://chase-campus-store.streamlit.app *(password protected; instructor
access sent privately)*

## Files
- `app.py` - the Streamlit app
- `database.py` - functions that read from and write to Supabase
- `config.py` - loads the Supabase URL, secret key, and app password from Streamlit
  secrets, or from `.env` when running on my computer
- `requirements.txt` - packages to install
- `.env.example` and `.streamlit/secrets.toml.example` - templates with placeholder
  values only
- `.gitignore` - keeps `.env`, `.streamlit/secrets.toml`, and `.venv/` off GitHub
- `order_entry.py` - the old terminal version from the last assignment

## Running it locally
You need the Supabase project from class with the `customers`, `products`, and
`orders` tables already loaded.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and put in your project URL, your `sb_secret_` key, and a password of
your choice for `APP_PASSWORD`. Then run:

```bash
streamlit run app.py
```

## Deploying on Streamlit Community Cloud
1. Push the repo to GitHub (without `.env`).
2. Go to https://share.streamlit.io, click **Create app**, and choose this repository,
   the `main` branch, and `app.py` as the main file.
3. Under **Advanced settings > Secrets**, paste the three values from
   `.streamlit/secrets.toml.example` with the real ones filled in.
4. Click **Deploy**.

The app won't touch the database until the correct password is entered. If
`APP_PASSWORD` is missing, the app stays locked.

## How it works
1. **Data from Supabase.** The customer and product tables come from Supabase through
   the API, with prices shown as currency. **Refresh Data** loads everything again.
2. **Order entry.** Dropdowns show customer and product names. The app keeps the IDs
   for the insert. The quantity box only accepts whole numbers of 1 or more. A review
   table shows the customer, product, quantity, unit price, and total.
3. **Confirmation.** You have to tick the confirmation box and then click
   **Submit Order**. Clicking Submit without the box ticked shows a warning and saves
   nothing. The box's key includes the customer, product, quantity, and price, so
   changing any of them unticks it.
4. **Saving.** The insert only happens inside the Submit button's click, so a normal
   Streamlit rerun, a page refresh, or changing another widget can't create an
   order. Right before saving, the app gets the product's current price from Supabase
   again. If the price changed, it shows the new price and makes you confirm again.
   The order date is today's date and Supabase creates the order ID. Errors show a
   friendly message without any connection details, and the success message only
   appears after the insert works. After a successful order the form clears.
5. **Verification.** After saving, the app uses the new order ID to query Supabase
   again and shows that record in a "Saved Order" table. The total is calculated
   from the stored `unit_price`. If the save worked but this lookup fails, it says the
   order was saved but couldn't be verified, and it does not submit it again.
6. **Order history.** All orders from Supabase, newest first. It updates after each
   saved order and when you click Refresh Data.
7. **Extra credit.** The "Show orders for" dropdown in Order History filters to one
   customer and shows how many orders they have and their total value, using each
   order's stored price.

## Testing (deployed app)
Orders in the table before testing: ____ After testing: ____

| Test | Expected result | What happened |
|---|---|---|
| Open the deployed app | Loads after the password is entered | |
| Wrong password | Rejected, no data shown | |
| View customers and products | Records come from Supabase | |
| Invalid quantity (0, -2, 1.5) | Prevented or rejected | |
| Submit without confirmation | No order inserted | |
| Confirm and submit a valid order | Exactly one order inserted | |
| View the verification table | New order retrieved from Supabase | |
| Refresh the page / change another widget | Order not inserted again | |
| Refresh order history | Saved order still there | |
| Filter history by customer (extra credit) | Only that customer's orders and their total | |

### Screenshots
![Order entry interface](screenshots/order-entry.png)
![Verified order](screenshots/verified-order.png)

## References
- https://docs.streamlit.io/develop/api-reference
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- https://supabase.com/docs/reference/python/select
- https://supabase.com/docs/reference/python/insert
