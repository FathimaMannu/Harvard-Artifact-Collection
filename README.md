# README.md

# 🎨 Harvard's Artifacts Collection Web App

This Streamlit web application allows users to explore, collect, and analyze artifact data from the Harvard Art Museums API. The app provides functionalities to fetch artifact records, transform them, store them in an SQLite database, and run predefined or custom SQL queries.

---

## Features

1. **Dynamic Background**: Custom background image support with fallback.
2. **Data Collection**: Fetch up to 2,500 records per classification from the Harvard Art Museums API.
3. **Data Transformation**: Extracts metadata, media information, and color details for artifacts.
4. **SQLite Integration**: Store collected records in a local SQLite database (`museum.db`).
5. **Predefined SQL Queries**: 20 ready-to-run queries for data insights.
6. **Custom SQL Queries**: Execute any SQL query on the stored dataset.
7. **Visualization**: Numeric query results can be visualized using bar charts.

---

## Installation & Setup

1. Clone the repository or copy the project files.
2. Install required Python packages:

```bash
pip install streamlit pandas requests
```

3. Place a local background image named `bg1.png` or `bg.png` in the project folder (optional).
4. Run the Streamlit app:

```bash
streamlit run app.py
```

---

## Usage

1. Open the app in your browser (automatically opened by Streamlit).
2. Select a classification from the dropdown.
3. Click **Collect Data** to fetch records.
4. Click **Migrate to SQL** to prepare for database insertion.
5. Click **Insert Data** to save records into the SQLite database.
6. Use **SQL Queries** to run predefined or custom queries and visualize results.

---

## Database Structure

### Tables:

- **artifact_metadata**
  - `id`, `title`, `culture`, `period`, `century`, `medium`, `dimensions`, `description`, `department`, `classification`, `accessionyear`, `accessionmethod`

- **artifact_media**
  - `objectid`, `imagecount`, `mediacount`, `colorcount`, `rank`, `datebegin`, `dateend`

- **artifact_colors**
  - `objectid`, `color`, `spectrum`, `hue`, `percent`, `css3`

---

## API Configuration

Default API Key is stored as `DEFAULT_API_KEY`. Replace it with your own key if necessary:

```python
DEFAULT_API_KEY = "your_api_key_here"
```

Endpoints:
- Objects: `https://api.harvardartmuseums.org/object`
- Classifications: `https://api.harvardartmuseums.org/classification`

---

## Predefined Queries

20 queries are available, including:
- Artifacts by century and culture
- Artifact counts per department
- Top colors and mediums
- Artifacts without description or accession method
- Average colors per artifact
- Artifacts per classification

---

## Requirements

```text
streamlit
pandas
requests
sqlite3 (built-in)
base64 (built-in)
os (built-in)
time (built-in)
```

---

## Notes

- Data collection may take several minutes depending on classification and record limits.
- Ensure a stable internet connection for API access.
- The database (`museum.db`) is created in the project directory automatically.

---



