import streamlit as st

st.set_page_config(
    page_title="Test App",
    layout="wide"
)

st.title("🚀 Test App Working!")

# Test if we can import
try:
    import gspread
    st.success("✅ gspread imported successfully")
except Exception as e:
    st.error(f"❌ gspread import failed: {e}")

try:
    from oauth2client.service_account import ServiceAccountCredentials
    st.success("✅ oauth2client imported successfully")
except Exception as e:
    st.error(f"❌ oauth2client import failed: {e}")

try:
    import pandas as pd
    st.success("✅ pandas imported successfully")
except Exception as e:
    st.error(f"❌ pandas import failed: {e}")

# Check secrets
st.subheader("🔑 Checking Secrets")
if 'google_credentials' in st.secrets:
    st.success("✅ Google credentials found in secrets")
    st.write("Keys available:", list(st.secrets['google_credentials'].keys()))
else:
    st.error("❌ Google credentials NOT found in secrets")
    
if 'SENDER_EMAIL' in st.secrets:
    st.success("✅ SENDER_EMAIL found in secrets")
else:
    st.warning("⚠️ SENDER_EMAIL not in secrets (optional)")
    
if 'SENDER_PASSWORD' in st.secrets:
    st.success("✅ SENDER_PASSWORD found in secrets")
else:
    st.warning("⚠️ SENDER_PASSWORD not in secrets (optional)")
