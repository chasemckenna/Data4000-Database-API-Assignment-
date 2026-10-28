"""Read configuration without printing credentials.
On Streamlit Community Cloud the values come from the app's Secrets settings.
On my computer they come from the .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def read_setting(name):
    # Try Streamlit secrets first, then fall back to environment variables / .env
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # No secrets.toml locally, so st.secrets raises an error. That's fine.
        pass
    load_dotenv(Path(__file__).with_name(".env"))
    return os.getenv(name, "")


def get_settings():
    url = read_setting("SUPABASE_URL").strip().rstrip("/")
    key = read_setting("SUPABASE_SECRET_KEY").strip()
    if not url.startswith("https://") or "YOUR_PROJECT" in url:
        raise ValueError("Set your project HTTPS URL in .env or Streamlit secrets (not the dashboard URL).")
    if not key.startswith("sb_secret_"):
        raise ValueError("Set SUPABASE_SECRET_KEY to your own project's sb_secret_ key.")
    return url, key


def get_app_password():
    return read_setting("APP_PASSWORD").strip()
