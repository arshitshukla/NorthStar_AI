import streamlit as st
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# 1. Supabase Connection
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# 2. Page Config
st.set_page_config(page_title="Sentinel Crisis Dashboard", layout="wide")
st.title("🚨 Sentinel: Real-Time Emergency Signals")
st.markdown("---")

# 3. Fetch Data Function
def get_data():
    response = supabase.table("emergency_reports").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(response.data)

# 4. Sidebar for Filters
st.sidebar.header("Control Panel")
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# 5. Main Dashboard Logic
df = get_data()

if not df.empty:
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Emergencies", len(df))
    col2.metric("High Urgency (>7)", len(df[df['urgency_score'] > 7]))
    col3.metric("Latest Signal", df.iloc[0]['location'] if 'location' in df.columns else "Unknown")

    st.subheader("Live Emergency Feed")
    
    # Clean up display
    display_df = df[['created_at', 'user_handle', 'resource', 'location', 'urgency_score', 'content']]
    
    # Highlight high urgency rows
    st.dataframe(
        display_df.style.highlight_max(axis=0, subset=['urgency_score'], color='#ff4b4b'),
        use_container_width=True
    )
    
    st.success("✅ Dashboard connected to live Supabase cluster.")
else:
    st.info("Waiting for incoming signals... Run your scraper to see data!")