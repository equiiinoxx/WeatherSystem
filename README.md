# Weather Data Analysis System

An end-to-end meteorological data exploration and analysis platform developed for academic evaluation. The system ingests, validates, analyzes, and visualizes recorded weather observations across time without relying on third-party cloud services or external forecasting APIs.

---

## 📌 Project Overview & Objectives

- **Difficulty Level:** Beginner / Academic College Project
- **Primary Objective:** Explore recorded weather observations and summarize temperature, humidity, and rainfall patterns over time.
- **Scope & Boundaries:**
  - Performs retrospective exploratory data analysis on **historical/recorded weather observations**.
  - **Non-Forecasting System:** Strictly analyzes recorded data; does not perform predictive forecasting.
- **Documented Units:**
  - **Temperature:** Degrees Celsius (`°C`)
  - **Humidity:** Percentage (`%`)
  - **Rainfall:** Millimeters (`mm`)

---

## 🛠️ Complete Tech Stack & Architecture

| Layer | Technology | Purpose & Responsibility |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3 (Flask) | Lightweight WSGI web server, REST API routing, file upload handling |
| **Data Processing** | Pandas | Date parsing, schema validation, data cleaning, monthly grouping |
| **Numerical Statistics**| NumPy | High-performance calculations: Min, Max, and Mean (`np.min`, `np.max`, `np.mean`) |
| **Data Visualization** | Matplotlib | Generates Temperature Trend line charts & Rainfall Comparison bar charts |
| **Database** | SQL (MySQL Server) | Persistent storage for validated observations (`weather_records` table) |
| **Environment Management** | python-dotenv | Securely loads database credentials from `.env` without exposing secrets |
| **Frontend UI** | HTML5 & CSS3 | Industrial responsive dashboard with KPI metrics and sticky navigation |
| **Frontend Logic** | JavaScript (ES6) | Asynchronous API communication (`fetch`), drag-and-drop file ingestion, dynamic DOM rendering |

---

## 🏗️ Project Folder Structure

```
WeatherSystem/
│
├── 📁 backend/
│   ├── app.py                  # Main Flask application and REST API endpoints
│   ├── database.py             # MySQL connection manager & CRUD queries
│   ├── analysis.py             # Data validation, Pandas/NumPy computation & Matplotlib plotting
│   ├── requirements.txt        # Python package dependency list
│   └── .env                    # Local database configuration (host, user, password)
│
├── 📁 frontend/
│   ├── index.html              # Dashboard user interface
│   ├── 📁 css/
│   │   └── style.css           # Styling system & responsive layout
│   └── 📁 js/
│       └── script.js           # Client-side event handling & UI rendering
│
├── 📁 data/
│   └── sample_weather_data.csv # Public sample dataset (includes intentional validation test rows)
│
├── 📁 database/
│   └── schema.sql              # Raw SQL table creation script
│
├── 📁 venv/                    # Isolated Python virtual environment
├── .env.example                # Configuration template
├── run.py                      # Root launcher script
└── README.md                   # Comprehensive project documentation
```

---

## 🗄️ Database Entity & Schema

The system automatically verifies and creates the database and table upon startup.

- **Database Name:** `weather_analysis`
- **Table Name:** `weather_records`

```sql
CREATE DATABASE IF NOT EXISTS weather_analysis;
USE weather_analysis;

CREATE TABLE IF NOT EXISTS weather_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    observation_date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    rainfall FLOAT
);
```

---

## 🚀 Step-by-Step Running Guide

Follow these steps to run the application completely self-contained on any computer:

### Step 1: Ensure Prerequisites Are Installed
- **Python 3.10+** installed on the computer.
- **MySQL Server** installed and running on the local machine (e.g., MySQL 8.0).

---

### Step 2: Configure Database Credentials
Open `backend/.env` (or copy `.env.example` to `backend/.env`) and verify your local MySQL credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=weather_analysis
```

---

### Step 3: Activate the Virtual Environment
Open your terminal inside the project directory:

- **Windows PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell shows a script execution warning, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the command again)*

- **Windows Command Prompt (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

- **Git Bash / Linux / macOS:**
  ```bash
  source venv/Scripts/activate
  ```

Your terminal prompt will indicate `(venv)` once activated.

*(Note: If setting up on a brand new computer without `venv`, create and install with: `python -m venv venv` and `.\venv\Scripts\pip install -r backend/requirements.txt`)*

---

### Step 4: Start the Application
Run the launcher script from the root directory:

```bash
python run.py
```

You will see:
```
============================================================
🚀 Starting Weather Data Analysis System Backend...
📍 Local URL: http://127.0.0.1:5000
============================================================
Database and table initialized successfully.
```

---

### Step 5: Open the Dashboard in Your Browser
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🎯 Key Features to Demonstrate During Presentation

### 1. Ingestion Station & Data Validation
- Click **"📂 Ingest Bundled Sample Dataset"** (or drag & drop `data/sample_weather_data.csv`).
- **Show the File Staging Badge:** Point out the file name, size indicator, and the **✕ remove button** to clear a staged file.

### 2. Transparent Data-Quality Report (Key Acceptance Criterion)
- Point out the **KPI Cards**:
  - Total Ingested Observations (40)
  - Valid Records Stored (36)
  - Anomalies Quarantined (4)
  - Quality Pass Rate (90%)
- Scroll to the **Quarantined Observation Log**: Show that invalid rows in the CSV are **not ignored silently**; they are transparently audited with exact row numbers and explanations:
  - *Row 37:* Invalid date format (`2023-13-45`)
  - *Row 38:* Non-numeric temperature (`abc`)
  - *Row 39:* Negative humidity (`-10%`)
  - *Row 40:* Negative rainfall (`-5 mm`)

### 3. Meteorological Visual Analytics (Matplotlib Engine)
- **Temperature Trend Chart:** Displays Minimum (blue), Mean (dashed orange), and Maximum (red) temperature trajectories across observation months.
- **Rainfall Comparison Chart:** Displays cumulative monthly rainfall with exact data labels on each bar.
- Highlight that chart titles **dynamically identify the location and time period** (e.g., `Seattle (Jan 2023 - Dec 2023)`).
- Click the **"⬇️ Save Plot"** button to show that generated charts can be downloaded directly as PNG images.

### 4. Monthly Weather Summary (Pandas & NumPy)
- Show the table comparing monthly Min, Max, and Avg values for temperature, humidity, and rainfall.
- Type in the **Filter Search Box** (e.g., "Jul" or "Seattle") to demonstrate real-time table filtering.

### 5. Single Source of Truth & Database Persistence
- Scroll to the **MySQL Live Explorer** section showing records directly from the `weather_records` table.
- **Refresh the browser (F5):** Demonstrate that **all data, charts, and tables persist** because the application loads the current state directly from MySQL on page load.
- Click **"🗑️ Clear DB"** to demonstrate table truncation (`TRUNCATE TABLE weather_records`), resetting the database cleanly.

---

## 💡 Viva / Presentation Q&A Preparation

### Q1: Why use a relational database (MySQL) when the data originates from a CSV?
> **Answer:** In real-world data pipelines, CSV files are transient input streams. Storing validated records in MySQL ensures data integrity, prevents duplicate entries via keys, provides ACID transactions, and enables historical querying across multiple ingestion batches.

### Q2: How does the system handle missing or corrupted data?
> **Answer:** The system uses strict schema validation in Python (`analysis.py`). Rather than crashing or silently altering data, it quarantines problematic rows, logs the specific violation reason (e.g., non-numeric string, out-of-range value, invalid date), and reports them transparently in the Data-Quality Audit section.

### Q3: Why does this system avoid forecasting?
> **Answer:** Meteorological forecasting requires numerical weather prediction (NWP) models, satellite assimilation, and differential equations. This system's objective is strictly descriptive and exploratory data analysis (EDA) of recorded historical observations.

### Q4: How are the charts rendered without saving files to the hard drive?
> **Answer:** Matplotlib runs in headless mode (`Agg` backend). Figures are rendered in-memory into a binary byte buffer (`io.BytesIO`), encoded into Base64 format, and transmitted directly as data URIs to the browser frontend. This eliminates disk I/O bottlenecks and file permission errors.
