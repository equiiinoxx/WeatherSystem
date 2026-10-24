# Weather Data Analysis System

An organized, beginner-friendly college project that explores recorded weather observations and summarizes temperature, humidity, and rainfall patterns over time.

> **Scope Note:** This system performs exploratory analysis on recorded historical weather observations. It does not perform weather forecasting.

---

## 🏗️ Project Architecture

```
WheatherSystem/
├── backend/
│   ├── app.py                  # Flask backend API server
│   ├── database.py             # MySQL database connection & CRUD operations
│   ├── analysis.py             # Pandas & NumPy analysis, Matplotlib charts
│   └── requirements.txt        # Python backend dependencies
├── frontend/
│   ├── index.html              # HTML5 dashboard
│   ├── css/
│   │   └── style.css           # Clean CSS styling
│   └── js/
│       └── script.js           # Client-side JavaScript logic
├── data/
│   └── sample_weather_data.csv # Bundled test dataset with valid & invalid rows
├── database/
│   └── schema.sql              # MySQL database & table creation script
├── run.py                      # Root launcher script
└── README.md                   # Project documentation
```

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask, Pandas, NumPy, Matplotlib)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla ES6)
- **Database:** SQL (MySQL)

---

## 📋 Features Implemented

1. **Upload Weather CSV File:**
   - Upload any CSV file with recorded weather observations.
   - Built-in **"Load Bundled Sample Data"** button for instant testing.
2. **Field Validation & Data Quality Report:**
   - Validates `observation_date` (standard date format parsing).
   - Validates `temperature` (numeric, realistic range -60°C to 60°C).
   - Validates `humidity` (numeric, 0% to 100%).
   - Validates `rainfall` (numeric, >= 0 mm).
   - **Transparent Data-Quality Report:** Records containing missing or invalid values are transparently logged with row numbers and exact reasons.
3. **Monthly Weather Statistics (Pandas & NumPy):**
   - Monthly grouping with Pandas.
   - Calculates **Minimum**, **Maximum**, and **Average** for Temperature, Humidity, and Rainfall using NumPy statistics (`np.min`, `np.max`, `np.mean`).
4. **Weather Trend Visualizations (Matplotlib):**
   - **Temperature Trend Chart:** Matplotlib line chart displaying Min, Max, and Avg temperature trends across months.
   - **Rainfall Comparison Chart:** Matplotlib bar chart comparing monthly rainfall.
   - Charts dynamically display the observation **location** and **time period** in the title.
5. **Database Storage (MySQL):**
   - Stores validated weather records into MySQL table `weather_records`.
   - Built-in viewer to inspect stored database rows.

---

## 🗄️ Database Schema

MySQL Table: `weather_records`

```sql
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

## 📏 Documented Units

- **Temperature:** Degrees Celsius (`°C`)
- **Humidity:** Percentage (`%`)
- **Rainfall:** Millimeters (`mm`)

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Verify Database Settings
Check `backend/database.py` for MySQL credentials (default configured for `localhost`, user `root`, database `weather_analysis`).

### 3. Run the Application
From the root directory:
```bash
python run.py
```
*(Or navigate to `backend/` and run `python app.py`)*

### 4. Open in Browser
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```
*(If opening `frontend/index.html` via VS Code Live Server on port 5500, it automatically connects to the Flask backend on port 5000)*
