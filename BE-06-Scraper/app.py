import asyncio
import json
import os
import sys
from datetime import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import func

# Windows asyncio Proactor socket shutdown fix to silence WinError 10054 connection reset on shutdown
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

        def _silenced_call_connection_lost(self, exc):
            try:
                _orig_call_connection_lost(self, exc)
            except (ConnectionResetError, OSError):
                pass

        _ProactorBasePipeTransport._call_connection_lost = _silenced_call_connection_lost
    except Exception:
        pass

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import settings
from core.exceptions import InvalidSearchLocationError, ScraperError
from storage.database import SessionLocal
from storage.models import Book, Dataset, Lead, ScrapeLog
from targets.books_target import BooksTargetStrategy
from targets.kaggle_target import KaggleTargetStrategy
from targets.leads_target import LeadsTargetStrategy

# Page Configuration
st.set_page_config(
    page_title="Flyrank BE-06 | Multi-Target Web Scraper",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #6B7280;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def run_async(coro):
    """Safely run async coroutines on Windows without Proactor loop shutdown hang."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(coro)


def get_db_metrics():
    db = SessionLocal()
    try:
        books_count = db.query(func.count(Book.upc)).scalar() or 0
        leads_count = db.query(func.count(Lead.id)).scalar() or 0
        datasets_count = db.query(func.count(Dataset.dataset_url)).scalar() or 0
        sessions_count = db.query(func.count(ScrapeLog.session_id)).scalar() or 0
        return books_count, leads_count, datasets_count, sessions_count
    finally:
        db.close()


def records_to_dataframe(records: list, target_key: str) -> pd.DataFrame:
    """Convert raw Pydantic record list from direct scrape run into a clean DataFrame."""
    if not records:
        return pd.DataFrame()

    if target_key == "books":
        data = [
            {
                "UPC": b.upc,
                "Title": b.title,
                "Category": b.category,
                "Price (£)": float(b.price_incl_tax),
                "Rating (1-5)": b.rating,
                "Availability": b.availability_status,
                "Stock": b.stock_quantity,
                "URL": b.product_page_url,
            }
            for b in records
        ]
    elif target_key == "leads":
        data = [
            {
                "ID": l.id,
                "Business Name": l.business_name,
                "Category": l.category_industry or "Local Business",
                "Address": f"{l.street_name} {l.house_number or ''}".strip(),
                "City": l.city,
                "Phone": l.phone_number or "N/A",
                "Website": l.website_url or "N/A",
                "Type": "Business" if l.is_business else "Person",
            }
            for l in records
        ]
    elif target_key == "kaggle":
        data = [
            {
                "Title": d.dataset_title,
                "Creator": d.creator_username or "N/A",
                "Upvotes": d.upvotes_count,
                "Views": d.views_count,
                "Downloads": d.downloads_count,
                "License": d.license_name or "N/A",
                "Tags": str(d.tags),
                "URL": d.dataset_url,
            }
            for d in records
        ]
    else:
        data = []

    return pd.DataFrame(data)


def load_table_data(target_name: str, city_filter: str | None = None) -> pd.DataFrame:
    db = SessionLocal()
    try:
        if target_name == "books":
            query = db.query(Book).order_by(Book.updated_at.desc()).all()
            data = [
                {
                    "UPC": b.upc,
                    "Title": b.title,
                    "Category": b.category,
                    "Price (£)": float(b.price_incl_tax),
                    "Rating (1-5)": b.rating,
                    "Availability": b.availability_status,
                    "Stock": b.stock_quantity,
                    "URL": b.product_page_url,
                }
                for b in query
            ]
        elif target_name == "leads":
            q = db.query(Lead)
            if city_filter and city_filter != "All Cities":
                q = q.filter(Lead.city.ilike(f"%{city_filter}%"))
            query = q.order_by(Lead.updated_at.desc()).all()
            data = [
                {
                    "ID": l.id,
                    "Business Name": l.business_name,
                    "Category": l.category_industry or "Local Business",
                    "Address": f"{l.street_name} {l.house_number or ''}".strip(),
                    "City": l.city,
                    "Phone": l.phone_number or "N/A",
                    "Website": l.website_url or "N/A",
                    "Type": "Business" if l.is_business else "Person",
                    "Last Updated": l.updated_at.strftime("%H:%M:%S") if l.updated_at else "",
                }
                for l in query
            ]
        elif target_name == "kaggle":
            query = db.query(Dataset).order_by(Dataset.updated_at.desc()).all()
            data = [
                {
                    "Title": d.dataset_title,
                    "Creator": d.creator_username or "N/A",
                    "Upvotes": d.upvotes_count,
                    "Views": d.views_count,
                    "Downloads": d.downloads_count,
                    "License": d.license_name or "N/A",
                    "Tags": d.tags or "[]",
                    "URL": d.dataset_url,
                }
                for d in query
            ]
        else:
            data = []

        return pd.DataFrame(data)
    finally:
        db.close()


def load_scrape_logs() -> pd.DataFrame:
    db = SessionLocal()
    try:
        logs = db.query(ScrapeLog).order_by(ScrapeLog.start_time.desc()).all()
        data = [
            {
                "Session ID": l.session_id,
                "Target": l.target_name.upper(),
                "Start Time": l.start_time.strftime("%Y-%m-%d %H:%M:%S") if l.start_time else "N/A",
                "End Time": l.end_time.strftime("%Y-%m-%d %H:%M:%S") if l.end_time else "Running...",
                "Pages Scraped": l.total_pages_scraped,
                "Records Extracted": l.total_records_extracted,
                "Errors": l.error_count,
                "Status": l.status,
            }
            for l in logs
        ]
        return pd.DataFrame(data)
    finally:
        db.close()


# Title Header
st.markdown('<div class="main-header">🕷️ BE-06-Scraper | Multi-Target Web Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Unified SQLite-First ETL Pipeline with Politeness Engine & Database Persistence</div>', unsafe_allow_html=True)

# Top Metrics Row
books_cnt, leads_cnt, datasets_cnt, sessions_cnt = get_db_metrics()
m1, m2, m3, m4 = st.columns(4)
m1.metric("📚 Books in DB", books_cnt)
m2.metric("🏢 B2B Leads in DB", leads_cnt)
m3.metric("🤖 Kaggle Datasets in DB", datasets_cnt)
m4.metric("📜 Total Scrape Sessions", sessions_cnt)

st.markdown("---")

# Sidebar Controls
st.sidebar.header("⚙️ Scraper Controls")
target_choice = st.sidebar.selectbox(
    "Select Target Scraper Strategy",
    options=["📚 Books (books.toscrape.com)", "🏢 B2B Leads (dasoertliche.de)", "🤖 Kaggle ML Datasets (kaggle.com)"],
    index=0,
)

if "Books" in target_choice:
    target_key = "books"
    st.sidebar.subheader("📚 Books Options")
    max_pages = st.sidebar.slider("Max Catalog Pages to Scrape", min_value=1, max_value=5, value=1)
    extra_params = {"max_pages": max_pages}

elif "Leads" in target_choice:
    target_key = "leads"
    st.sidebar.subheader("🏢 German B2B Leads Options")

    if "city_input_val" not in st.session_state:
        st.session_state["city_input_val"] = "Berlin"
    if "street_input_val" not in st.session_state:
        st.session_state["street_input_val"] = "Berliner Allee"

    def on_preset_change():
        preset = st.session_state.get("preset_choice", "")
        if preset and preset != "Custom Input (Type below)":
            parts = preset.split(" + ")
            if len(parts) == 2:
                st.session_state["city_input_val"] = parts[0]
                st.session_state["street_input_val"] = parts[1]

    st.sidebar.selectbox(
        "Quick Test City+Street Presets",
        options=[
            "Custom Input (Type below)",
            "Neu-Isenburg + Frankfurter Straße",
            "Freiburg + Willy-Brandt-Allee",
            "Frankfurt am Main + Ludwig Erhard Anlage",
            "Bad Homburg von der Höhe + Kaiser-Friedrich-Promenade",
            "Dietzenbach + Max Planck Straße",
            "Dietzenbach + Babenhäuser Straße",
            "Dietzenbach + Frankfurter Straße",
            "Berlin + Berliner Allee",
            "Berlin + Friedrichstraße",
            "München + Leopoldstraße",
            "Hamburg + Reeperbahn",
        ],
        key="preset_choice",
        on_change=on_preset_change,
    )

    city_val = st.sidebar.text_input("City Name", key="city_input_val")
    street_val = st.sidebar.text_input("Street Name", key="street_input_val")
    max_pages = st.sidebar.slider("Max Search Result Pages", min_value=1, max_value=3, value=1)
    extra_params = {"city": city_val, "street": street_val, "max_pages": max_pages}

else:
    target_key = "kaggle"
    st.sidebar.subheader("🤖 Kaggle ML Datasets Options")
    query_input = st.sidebar.text_input("Dataset Search Query", value="machine learning")
    limit_input = st.sidebar.slider("Dataset Items Limit", min_value=1, max_value=20, value=5)
    extra_params = {"query": query_input, "limit": limit_input, "max_pages": 1}

# Politeness Info Box
st.sidebar.markdown("---")
st.sidebar.caption("🛡️ **Politeness Engine Settings**")
st.sidebar.caption(f"• **User-Agent**: `{settings.USER_AGENT[:35]}...`")
st.sidebar.caption(f"• **Rate Limit Delay**: `{settings.DEFAULT_RATE_LIMIT_DELAY}s` per request")
st.sidebar.caption("• **Storage Engine**: `SQLite (flyrank_scraper.db)`")

run_button = st.sidebar.button("🚀 Launch Live Scraper Strategy", type="primary")

# Session State for Latest Run Results
if "latest_run" not in st.session_state:
    st.session_state["latest_run"] = None

# Tabs Navigation
tab_data, tab_db, tab_inspector, tab_logs = st.tabs([
    "🎯 Direct Scrape Results",
    "🗄️ SQLite Database Explorer",
    "🔍 Detailed Record Inspector",
    "📜 Session Audit Logs"
])

# Trigger Scrape Execution
if run_button:
    with tab_data:
        st.info(f"Launching `{target_key.upper()}` scraper strategy with parameters: `{extra_params}`")
        with st.spinner("Fetching pages with politeness rate limiting and storing records to SQLite..."):
            try:
                if target_key == "books":
                    strategy = BooksTargetStrategy()
                elif target_key == "leads":
                    strategy = LeadsTargetStrategy()
                else:
                    strategy = KaggleTargetStrategy()

                records = run_async(strategy.run(**extra_params))
                st.session_state["latest_run"] = {
                    "target_key": target_key,
                    "params": extra_params,
                    "records": records,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
            except InvalidSearchLocationError as e:
                st.session_state["latest_run"] = None
                st.error(f"❌ Invalid Location Error: {e}")
            except ScraperError as e:
                st.session_state["latest_run"] = None
                st.error(f"❌ Scraper Error: {e}")
            except Exception as e:
                st.session_state["latest_run"] = None
                clean_err = str(e).split("\n")[0]
                st.error(f"❌ Scraping execution error: {clean_err}")

# TAB 1: Direct Scrape Results Only
with tab_data:
    latest = st.session_state.get("latest_run")
    if latest and latest.get("records"):
        t_key = latest["target_key"]
        p_info = latest["params"]
        r_list = latest["records"]
        ts = latest["timestamp"]

        st.subheader(f"🎯 Direct Results — `{t_key.upper()}` Scrape at `{ts}`")
        st.success(f"✅ Extracted **{len(r_list)}** fresh record(s) for parameters: `{p_info}`")

        df_direct = records_to_dataframe(r_list, t_key)
        st.dataframe(df_direct, hide_index=True)
        st.caption(f"Showing **ONLY the {len(r_list)} record(s)** extracted from this active scrape run.")
    else:
        st.info("ℹ️ No active scrape run output to display. Configure parameters in the sidebar and click **🚀 Launch Live Scraper Strategy**!")

# TAB 2: Full Database Explorer
with tab_db:
    col_t, col_f = st.columns([3, 1])
    with col_t:
        st.subheader(f"🗄️ SQLite Database Explorer — Target: `{target_key.upper()}`")
    with col_f:
        city_filter = None
        if target_key == "leads":
            db_s = SessionLocal()
            distinct_cities = [c[0] for c in db_s.query(Lead.city).distinct().all() if c[0]]
            db_s.close()
            city_filter = st.selectbox("Filter Historical City", options=["All Cities"] + distinct_cities, index=0)

    df_db = load_table_data(target_key, city_filter=city_filter)

    if not df_db.empty:
        st.dataframe(df_db, hide_index=True)
        st.caption(f"Showing **{len(df_db)}** total historical record(s) stored in SQLite database.")
    else:
        st.warning(f"No historical records found in SQLite database for `{target_key}`.")

# TAB 3: Detailed Record Inspector
with tab_inspector:
    st.subheader("🔍 Record Inspector & Structured Metadata Viewer")
    db = SessionLocal()
    try:
        if target_key == "books":
            items = db.query(Book).order_by(Book.updated_at.desc()).all()
            if items:
                selected_item = st.selectbox("Select Book Record", options=items, format_func=lambda x: f"[{x.upc}] {x.title}")
                if selected_item:
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.markdown("##### 📌 Structured Fields")
                        st.write(f"**Title**: {selected_item.title}")
                        st.write(f"**Category**: {selected_item.category}")
                        st.write(f"**Price (incl. tax)**: £{selected_item.price_incl_tax:.2f}")
                        st.write(f"**Rating**: ⭐ {selected_item.rating} / 5")
                        st.write(f"**Stock**: {selected_item.stock_quantity} available ({selected_item.availability_status})")
                        st.write(f"**UPC**: `{selected_item.upc}`")
                    with col_right:
                        st.markdown("##### 📝 Description & Detail URL")
                        st.write(selected_item.description or "No description available.")
                        st.markdown(f"[🔗 View Original Product Page]({selected_item.product_page_url})")

        elif target_key == "leads":
            items = db.query(Lead).order_by(Lead.updated_at.desc()).all()
            if items:
                selected_item = st.selectbox("Select Lead Record", options=items, format_func=lambda x: f"[{x.id}] {x.business_name} ({x.city} - {x.street_name})")
                if selected_item:
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.markdown("##### 🏢 Business Contact Details")
                        st.write(f"**Name**: {selected_item.business_name}")
                        st.write(f"**Industry**: {selected_item.category_industry}")
                        st.write(f"**Address**: {selected_item.street_name} {selected_item.house_number or ''}, {selected_item.postal_code or ''} {selected_item.city}")
                        st.write(f"**Phone**: `{selected_item.phone_number or 'N/A'}`")
                        st.write(f"**Website**: {selected_item.website_url or 'N/A'}")
                    with col_right:
                        st.markdown("##### 🏷️ Microdata Metadata")
                        st.write(f"**Entity ID**: `{selected_item.id}`")
                        st.write(f"**JSON-LD Type**: `{selected_item.raw_json_ld_type}`")
                        st.write(f"**Is Business Lead**: `{selected_item.is_business}`")
                        if selected_item.detail_page_url:
                            st.markdown(f"[🔗 Directory Detail Link]({selected_item.detail_page_url})")

        elif target_key == "kaggle":
            items = db.query(Dataset).order_by(Dataset.updated_at.desc()).all()
            if items:
                selected_item = st.selectbox("Select Kaggle Dataset Record", options=items, format_func=lambda x: f"{x.dataset_title} ({x.creator_username})")
                if selected_item:
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.markdown("##### 🤖 Dataset Metrics")
                        st.write(f"**Title**: {selected_item.dataset_title}")
                        st.write(f"**Creator**: `{selected_item.creator_username}`")
                        st.write(f"**Upvotes**: 👍 {selected_item.upvotes_count:,}")
                        st.write(f"**Views**: 👁️ {selected_item.views_count:,}")
                        st.write(f"**Downloads**: 📥 {selected_item.downloads_count:,}")
                        st.write(f"**License**: `{selected_item.license_name}`")
                    with col_right:
                        st.markdown("##### 📜 Description Summary & Tags")
                        st.write(selected_item.summary_description or "No description available.")
                        st.write(f"**Tags**: `{selected_item.tags}`")
                        st.markdown(f"[🔗 Kaggle Dataset Link]({selected_item.dataset_url})")
    finally:
        db.close()

# TAB 4: Audit Logs
with tab_logs:
    st.subheader("📜 Scraping Session Audit Trail (`scrape_logs` Table)")
    df_logs = load_scrape_logs()

    if not df_logs.empty:
        st.dataframe(df_logs, hide_index=True)
        st.caption(f"Displaying **{len(df_logs)}** audit session log(s) from SQLite database.")
    else:
        st.info("No session logs recorded yet. Launch a scraper strategy to generate audit logs!")
