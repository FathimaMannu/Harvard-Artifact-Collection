import time
import sqlite3
import requests
import pandas as pd
import streamlit as st
import base64
import os

# -------------------------
# Background helper
# -------------------------
def set_bg_from_local(preferred_names=("bg1.png", "bg.png")):
    for name in preferred_names:
        try:
            if os.path.isfile(name):
                with open(name, "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode()
                st.markdown(
                    f"""
                    <style>
                    [data-testid="stAppViewContainer"] {{
                        background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
                        background-size: cover;
                    }}
                    [data-testid="stHeader"], [data-testid="stSidebar"] {{
                        background: rgba(255, 255, 255, 0.7);
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                return True
        except Exception:
            pass

    # fallback image
    url = "https://images.unsplash.com/photo-1526401485004-2aa7f3b4a36a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80"
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("{url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"], [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.7);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return False

# -------------------------
# Config
# -------------------------
st.set_page_config(page_title="Harvard's Artifacts Collection", layout="wide", page_icon="🎨")
API_BASE = "https://api.harvardartmuseums.org"
OBJECT_ENDPOINT = f"{API_BASE}/object"
CLASS_ENDPOINT = f"{API_BASE}/classification"
DB_PATH = "museum.db"
DEFAULT_API_KEY = "9a00ef22-0bbb-4963-a30e-af65a44e0ec8"

# -------------------------
# DB Helpers
# -------------------------
def get_conn(path: str = DB_PATH):
    return sqlite3.connect(path, check_same_thread=False)

def init_db(conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS artifact_metadata (
        id INTEGER PRIMARY KEY,
        title TEXT,
        culture TEXT,
        period TEXT,
        century TEXT,
        medium TEXT,
        dimensions TEXT,
        description TEXT,
        department TEXT,
        classification TEXT,
        accessionyear INTEGER,
        accessionmethod TEXT
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS artifact_media (
        objectid INTEGER PRIMARY KEY,
        imagecount INTEGER,
        mediacount INTEGER,
        colorcount INTEGER,
        rank INTEGER,
        datebegin INTEGER,
        dateend INTEGER
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS artifact_colors (
        objectid INTEGER,
        color TEXT,
        spectrum TEXT,
        hue TEXT,
        percent REAL,
        css3 TEXT
    );""")
    conn.commit()

# -------------------------
# API Fetch + Transform
# -------------------------
def get_all_classifications():
    params = {"apikey": DEFAULT_API_KEY, "size": 100}
    resp = requests.get(CLASS_ENDPOINT, params=params)
    if resp.status_code == 200:
        data = resp.json()
        return sorted([rec["name"] for rec in data.get("records", [])])
    return ["Prints", "Paintings", "Drawings", "Sculpture", "Coins"]  # fallback

def fetch_objects(api_key, classification, page_size=100, limit=2500):
    records = []
    page = 1
    while len(records) < limit:
        params = {
            "apikey": api_key,
            "classification": classification,
            "size": page_size,
            "page": page
        }
        resp = requests.get(OBJECT_ENDPOINT, params=params)
        if resp.status_code != 200:
            break
        data = resp.json()
        recs = data.get("records", [])
        if not recs:
            break
        records.extend(recs)
        if len(records) >= limit:
            records = records[:limit]
            break
        page += 1
        time.sleep(0.2)
    return records

def safe_get(d, key, default=None):
    return d.get(key, default)

def transform_records(records):
    meta_rows, media_rows, color_rows = [], [], []
    for r in records:
        obj_id = safe_get(r, "id")
        meta_rows.append({
            "id": obj_id,
            "title": safe_get(r, "title"),
            "culture": safe_get(r, "culture"),
            "period": safe_get(r, "period"),
            "century": safe_get(r, "century"),
            "medium": safe_get(r, "medium"),
            "dimensions": safe_get(r, "dimensions"),
            "description": safe_get(r, "description"),
            "department": safe_get(r, "department"),
            "classification": safe_get(r, "classification"),
            "accessionyear": safe_get(r, "accessionyear"),
            "accessionmethod": safe_get(r, "accessionmethod"),
        })
        colors = safe_get(r, "colors", []) or []
        media_rows.append({
            "objectid": obj_id,
            "imagecount": safe_get(r, "imagecount"),
            "mediacount": safe_get(r, "mediacount"),
            "colorcount": len(colors),
            "rank": safe_get(r, "rank"),
            "datebegin": safe_get(r, "datebegin"),
            "dateend": safe_get(r, "dateend"),
        })
        for c in colors:
            color_rows.append({
                "objectid": obj_id,
                "color": safe_get(c, "color"),
                "spectrum": safe_get(c, "spectrum"),
                "hue": safe_get(c, "hue"),
                "percent": safe_get(c, "percent"),
                "css3": safe_get(c, "css3"),
            })
    return pd.DataFrame(meta_rows), pd.DataFrame(media_rows), pd.DataFrame(color_rows)

# -------------------------
# Predefined Queries (20)
# -------------------------
QUERIES = {
    "Artifacts from 11th century & Byzantine culture": 
        "SELECT * FROM artifact_metadata WHERE century LIKE '%11th%' AND culture LIKE '%Byzantine%';",
    "Artifacts count per department": 
        "SELECT department, COUNT(*) as cnt FROM artifact_metadata GROUP BY department;",
    "Top 5 most used colors": 
        "SELECT color, COUNT(*) as freq FROM artifact_colors GROUP BY color ORDER BY freq DESC LIMIT 5;",
    "Artifacts per classification + avg media count": 
        "SELECT classification, COUNT(*) as cnt, AVG(mediacount) as avg_media FROM artifact_metadata meta JOIN artifact_media m ON meta.id=m.objectid GROUP BY classification;",
    "Artifacts created between 1200 and 1500": 
        "SELECT * FROM artifact_media WHERE datebegin>=1200 AND dateend<=1500;",
    "Top 10 cultures by artifact count": 
        "SELECT culture, COUNT(*) as cnt FROM artifact_metadata GROUP BY culture ORDER BY cnt DESC LIMIT 10;",
    "Artifacts with missing description": 
        "SELECT * FROM artifact_metadata WHERE description IS NULL OR description='';",
    "Artifacts with dimensions info": 
        "SELECT * FROM artifact_metadata WHERE dimensions IS NOT NULL LIMIT 10;",
    "Artifacts ranked highest": 
        "SELECT id, title, rank FROM artifact_metadata meta JOIN artifact_media m ON meta.id=m.objectid ORDER BY rank DESC LIMIT 10;",
    "Average colors per artifact": 
        "SELECT AVG(colorcount) as avg_colors FROM artifact_media;",
    "Most frequent medium": 
        "SELECT medium, COUNT(*) as cnt FROM artifact_metadata GROUP BY medium ORDER BY cnt DESC LIMIT 5;",
    "Artifacts per century": 
        "SELECT century, COUNT(*) as cnt FROM artifact_metadata GROUP BY century ORDER BY cnt DESC;",
    "Departments with >100 artifacts": 
        "SELECT department, COUNT(*) as cnt FROM artifact_metadata GROUP BY department HAVING cnt>100;",
    "Top 5 accessions by year": 
        "SELECT accessionyear, COUNT(*) as cnt FROM artifact_metadata GROUP BY accessionyear ORDER BY cnt DESC LIMIT 5;",
    "Artifacts without accession method": 
        "SELECT * FROM artifact_metadata WHERE accessionmethod IS NULL OR accessionmethod='';",
    "Classification distribution": 
        "SELECT classification, COUNT(*) as cnt FROM artifact_metadata GROUP BY classification;",
    "Artifacts per color spectrum": 
        "SELECT spectrum, COUNT(*) as cnt FROM artifact_colors GROUP BY spectrum;",
    "Artifacts with more than 3 colors": 
        "SELECT m.objectid, meta.title, m.colorcount FROM artifact_media m JOIN artifact_metadata meta ON m.objectid=meta.id WHERE colorcount>3;",
    "Earliest artifacts by datebegin": 
        "SELECT meta.id, meta.title, m.datebegin FROM artifact_metadata meta JOIN artifact_media m ON meta.id=m.objectid ORDER BY m.datebegin ASC LIMIT 10;",
    "Latest artifacts by dateend": 
        "SELECT meta.id, meta.title, m.dateend FROM artifact_metadata meta JOIN artifact_media m ON meta.id=m.objectid ORDER BY m.dateend DESC LIMIT 10;"
}

# -------------------------
# Streamlit App
# -------------------------
def main():
    set_bg_from_local()
    st.markdown("<h1 style='text-align:center;'>🎨🏛️ Harvard's Artifacts Collection</h1>", unsafe_allow_html=True)

    classifications = get_all_classifications()
    classification = st.selectbox(
        "Select a classification:",
        classifications,
        index=0,
        placeholder="Type to search (e.g., Paintings, Prints)"
    )

    col1, col2, col3, col4 = st.columns([1,1,1,1], gap="large")

    with col1:
        if st.button("Collect Data", use_container_width=True):
            records = fetch_objects(DEFAULT_API_KEY, classification)
            if records:
                st.session_state["records"] = records
                st.success(f"Collected {len(records)} records for {classification}")

                meta, media, colors = transform_records(records)
                tab1, tab2, tab3 = st.tabs(["📑 Metadata", "🖼️ Media", "🎨 Colors"])
                with tab1: st.dataframe(meta.head(10), use_container_width=True)
                with tab2: st.dataframe(media.head(10), use_container_width=True)
                with tab3: st.dataframe(colors.head(10), use_container_width=True)
            else:
                st.warning("No records found.")

    with col2:
        if st.button("Migrate to SQL", use_container_width=True):
            if "records" in st.session_state:
                st.session_state["migrate_ready"] = True
                st.info("Click 'Insert Data' to push collected records into DB.")

    with col3:
        if st.session_state.get("migrate_ready"):
            if st.button("Insert Data", use_container_width=True):
                conn = get_conn()
                init_db(conn)
                meta, media, colors = transform_records(st.session_state["records"])
                cur = conn.cursor()

                # ✅ Safe insert (no duplicate errors)
                for _, row in meta.drop_duplicates(subset=["id"]).iterrows():
                    cur.execute("""INSERT OR REPLACE INTO artifact_metadata 
                                   (id, title, culture, period, century, medium, dimensions,
                                    description, department, classification, accessionyear, accessionmethod)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                tuple(row))

                for _, row in media.drop_duplicates(subset=["objectid"]).iterrows():
                    cur.execute("""INSERT OR REPLACE INTO artifact_media 
                                   (objectid, imagecount, mediacount, colorcount, rank, datebegin, dateend)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                tuple(row))

                for _, row in colors.drop_duplicates().iterrows():
                    cur.execute("""INSERT OR REPLACE INTO artifact_colors 
                                   (objectid, color, spectrum, hue, percent, css3)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                tuple(row))

                conn.commit()
                st.success("✅ Data inserted into DB Sucessfully")

                # Preview inserted rows from DB
                st.subheader("📑 Recently Inserted Data (Preview)")
                preview_df = pd.read_sql_query("SELECT * FROM artifact_metadata ORDER BY id DESC LIMIT 10;", conn)
                st.dataframe(preview_df, use_container_width=True)

    with col4:
        if st.button("SQL Queries", use_container_width=True):
            st.session_state["sql_queries"] = not st.session_state.get("sql_queries", False)

    if st.session_state.get("sql_queries", False):
        st.subheader("📊 Run Predefined or Custom SQL Queries")
        query_name = st.selectbox("Choose a predefined query", list(QUERIES.keys()))
        if st.button("Run Selected Query", use_container_width=True):
            conn = get_conn()
            df = pd.read_sql_query(QUERIES[query_name], conn)
            st.dataframe(df, use_container_width=True)

            # ✅ Charts for all queries
            numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
            if len(numeric_cols) > 0:
                st.subheader("📈 Chart View")
                st.bar_chart(df[numeric_cols])

        custom_query = st.text_area("✍️ Write Your Own SQL Query")
        if st.button("Run Custom Query", use_container_width=True):
            if custom_query.strip():
                conn = get_conn()
                try:
                    df = pd.read_sql_query(custom_query, conn)
                    st.dataframe(df, use_container_width=True)
                    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
                    if len(numeric_cols) > 0:
                        st.subheader("📈 Chart View")
                        st.bar_chart(df[numeric_cols])
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
