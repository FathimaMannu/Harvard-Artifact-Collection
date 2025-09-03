# 🎨 Harvard's Artifacts Collection

This Streamlit app allows you to explore Harvard Art Museum's artifacts by classification, color, and other metadata. It fetches data from the Harvard Art Museums API, transforms it, and stores it in a local SQLite database for querying and analysis.

---

## Features

- Collect artifact records by classification (Prints, Paintings, Drawings, Sculpture, Coins, etc.)
- Store and manage data locally in SQLite database (`museum.db`)
- Transform API data into three tables: `artifact_metadata`, `artifact_media`, `artifact_colors`
- Run 20 predefined SQL queries for analysis
- Write and execute custom SQL queries
- Preview and visualize data using tables and charts
- Beautiful background and styled UI using Streamlit

---

## Requirements

- Python 3.9+
- Streamlit
- pandas
- requests
- sqlite3 (built-in)
- base64 (built-in)
- os (built-in)
- time (built-in)

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-link>
cd <your-repo-folder>
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Select a classification from the dropdown (e.g., Paintings, Prints).
3. Click **Collect Data** to fetch records from the Harvard Art Museums API.
4. Click **Migrate to SQL**, then **Insert Data** to save records into the local database.
5. Explore data using **SQL Queries**:
   - Select a predefined query or write a custom SQL query.
   - View results in table format and optional bar charts.

---

## Database Structure

### `artifact_metadata`
| Column           | Type    | Description                      |
|-----------------|---------|----------------------------------|
| id              | INTEGER | Artifact ID (Primary Key)        |
| title           | TEXT    | Artifact title                   |
| culture         | TEXT    | Culture                          |
| period          | TEXT    | Historical period                |
| century         | TEXT    | Century                          |
| medium          | TEXT    | Medium/material                  |
| dimensions      | TEXT    | Dimensions                       |
| description     | TEXT    | Description                      |
| department      | TEXT    | Department                       |
| classification  | TEXT    | Classification                   |
| accessionyear   | INTEGER | Year of accession                |
| accessionmethod | TEXT    | Method of accession              |

### `artifact_media`
| Column     | Type    | Description         |
|------------|---------|-------------------|
| objectid   | INTEGER | Artifact ID        |
| imagecount | INTEGER | Number of images  |
| mediacount | INTEGER | Media count       |
| colorcount | INTEGER | Number of colors |
| rank       | INTEGER | Rank              |
| datebegin  | INTEGER | Start date        |
| dateend    | INTEGER | End date          |

### `artifact_colors`
| Column    | Type   | Description      |
|-----------|--------|----------------|
| objectid  | INTEGER| Artifact ID     |
| color     | TEXT   | Color name      |
| spectrum  | TEXT   | Spectrum info   |
| hue       | TEXT   | Hue info        |
| percent   | REAL   | Percent coverage|
| css3      | TEXT   | CSS3 color code |

---

## Notes

- Default API key is set in the code. Replace `DEFAULT_API_KEY` with your own key if needed.
- Fetch limit per classification is 2,500 records to avoid API overloading.
- Background image can be customized using local images `bg1.png` or `bg.png`.

---

## License

MIT License
