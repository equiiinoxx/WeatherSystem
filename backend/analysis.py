import io
import base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend for web server
import matplotlib.pyplot as plt

# Documented Units
UNITS = {
    'temperature': '°C',
    'humidity': '%',
    'rainfall': 'mm'
}

def validate_and_clean_data(csv_file):
    """
    Validate date, temperature, humidity, and rainfall fields.
    Handles missing and invalid values transparently.
    Returns:
        valid_records: list of tuples for SQL insertion
        quality_report: dict containing validation statistics and issue logs
        df_valid: cleaned Pandas DataFrame
    """
    # Read CSV
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        return None, {"error": f"Failed to read CSV: {str(e)}"}, None

    # Expected column mapping (case-insensitive)
    cols = {c.strip().lower(): c for c in df.columns}
    
    # Required columns
    req_date = cols.get('observation_date') or cols.get('date')
    req_loc = cols.get('location') or cols.get('city')
    req_temp = cols.get('temperature') or cols.get('temp')
    req_hum = cols.get('humidity')
    req_rain = cols.get('rainfall') or cols.get('precipitation')

    if not all([req_date, req_loc, req_temp, req_hum, req_rain]):
        return None, {
            "error": "CSV must contain columns: observation_date, location, temperature, humidity, rainfall"
        }, None

    total_rows = len(df)
    valid_records = []
    issues = []
    valid_row_dicts = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-based index plus header row
        date_raw = str(row[req_date]).strip()
        loc_raw = str(row[req_loc]).strip()
        temp_raw = row[req_temp]
        hum_raw = row[req_hum]
        rain_raw = row[req_rain]

        row_errors = []

        # 1. Validate Date
        try:
            parsed_date = pd.to_datetime(date_raw, errors='raise').date()
            date_str = parsed_date.strftime('%Y-%m-%d')
        except Exception:
            row_errors.append(f"Invalid date format: '{date_raw}'")
            parsed_date = None

        # 2. Validate Location
        if not loc_raw or loc_raw.lower() in ['nan', 'null', 'none']:
            row_errors.append("Missing location")

        # 3. Validate Temperature (-60°C to +60°C)
        try:
            temp_val = float(temp_raw)
            if np.isnan(temp_val):
                row_errors.append("Missing temperature value")
            elif temp_val < -60 or temp_val > 60:
                row_errors.append(f"Temperature {temp_val}°C out of realistic range (-60 to 60°C)")
        except (ValueError, TypeError):
            row_errors.append(f"Invalid non-numeric temperature: '{temp_raw}'")
            temp_val = None

        # 4. Validate Humidity (0% to 100%)
        try:
            hum_val = float(hum_raw)
            if np.isnan(hum_val):
                row_errors.append("Missing humidity value")
            elif hum_val < 0 or hum_val > 100:
                row_errors.append(f"Humidity {hum_val}% out of range (0% to 100%)")
        except (ValueError, TypeError):
            row_errors.append(f"Invalid non-numeric humidity: '{hum_raw}'")
            hum_val = None

        # 5. Validate Rainfall (>= 0 mm)
        try:
            rain_val = float(rain_raw)
            if np.isnan(rain_val):
                row_errors.append("Missing rainfall value")
            elif rain_val < 0:
                row_errors.append(f"Rainfall {rain_val} mm cannot be negative")
        except (ValueError, TypeError):
            row_errors.append(f"Invalid non-numeric rainfall: '{rain_raw}'")
            rain_val = None

        # Transparent validation logging
        if row_errors:
            issues.append({
                "row": row_num,
                "reasons": row_errors,
                "raw_values": {
                    "date": date_raw,
                    "location": loc_raw,
                    "temp": str(temp_raw),
                    "humidity": str(hum_raw),
                    "rainfall": str(rain_raw)
                }
            })
        else:
            # Valid record for SQL & analysis
            valid_records.append((date_str, loc_raw, temp_val, hum_val, rain_val))
            valid_row_dicts.append({
                'observation_date': pd.to_datetime(date_str),
                'location': loc_raw,
                'temperature': temp_val,
                'humidity': hum_val,
                'rainfall': rain_val
            })

    df_valid = pd.DataFrame(valid_row_dicts)

    quality_report = {
        "total_records": total_rows,
        "valid_records": len(valid_records),
        "invalid_records": len(issues),
        "issues": issues,
        "units": {
            "temperature": "°C (Degrees Celsius)",
            "humidity": "% (Percentage)",
            "rainfall": "mm (Millimeters)"
        }
    }

    return valid_records, quality_report, df_valid


def calculate_weather_summary(df_valid):
    """
    Calculate monthly minimum, maximum, and average values using Pandas and NumPy.
    Also compares rainfall and temperature by month.
    """
    if df_valid.empty:
        return []

    # Ensure date sorting
    df_sorted = df_valid.sort_values('observation_date').copy()
    df_sorted['month'] = df_sorted['observation_date'].dt.strftime('%Y-%m')

    monthly_summary = []
    grouped = df_sorted.groupby(['month', 'location'])

    for (month, loc), group in grouped:
        # NumPy statistics
        t_arr = group['temperature'].to_numpy()
        h_arr = group['humidity'].to_numpy()
        r_arr = group['rainfall'].to_numpy()

        monthly_summary.append({
            'month': month,
            'location': loc,
            'days_observed': int(len(group)),
            'temp_min': round(float(np.min(t_arr)), 1),
            'temp_max': round(float(np.max(t_arr)), 1),
            'temp_avg': round(float(np.mean(t_arr)), 1),
            'humidity_min': round(float(np.min(h_arr)), 1),
            'humidity_max': round(float(np.max(h_arr)), 1),
            'humidity_avg': round(float(np.mean(h_arr)), 1),
            'rainfall_total': round(float(np.sum(r_arr)), 1),
            'rainfall_avg': round(float(np.mean(r_arr)), 1),
            'rainfall_max': round(float(np.max(r_arr)), 1)
        })

    return monthly_summary


def generate_weather_plots(df_valid):
    """
    Generate Temperature Trend (line chart) and Monthly Rainfall Comparison (bar chart)
    using Matplotlib.
    Charts explicitly identify location and period in their titles.
    Returns base64 encoded image strings.
    """
    if df_valid.empty:
        return None, None

    # Determine location and period for chart titles
    location = df_valid['location'].iloc[0]
    start_date = df_valid['observation_date'].min().strftime('%b %Y')
    end_date = df_valid['observation_date'].max().strftime('%b %Y')
    period_str = f"{start_date} - {end_date}" if start_date != end_date else start_date

    # Prepare monthly data
    df_sorted = df_valid.sort_values('observation_date').copy()
    df_sorted['month'] = df_sorted['observation_date'].dt.strftime('%b %Y')
    
    # Preserve month ordering
    months = df_sorted['month'].unique()
    
    monthly_temp_min = []
    monthly_temp_max = []
    monthly_temp_avg = []
    monthly_rainfall = []

    for m in months:
        subset = df_sorted[df_sorted['month'] == m]
        monthly_temp_min.append(np.min(subset['temperature']))
        monthly_temp_max.append(np.max(subset['temperature']))
        monthly_temp_avg.append(np.mean(subset['temperature']))
        monthly_rainfall.append(np.sum(subset['rainfall']))

    # 1. Temperature Trend Plot (Line Chart)
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=100)
    ax.plot(months, monthly_temp_max, marker='o', color='#e74c3c', label='Max Temp (°C)', linewidth=2)
    ax.plot(months, monthly_temp_avg, marker='s', color='#e67e22', label='Avg Temp (°C)', linewidth=2, linestyle='--')
    ax.plot(months, monthly_temp_min, marker='^', color='#3498db', label='Min Temp (°C)', linewidth=2)

    ax.set_title(f'Temperature Trends: {location} ({period_str})', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Month', fontsize=11, labelpad=8)
    ax.set_ylabel('Temperature (°C)', fontsize=11, labelpad=8)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='best')
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()

    buf_temp = io.BytesIO()
    plt.savefig(buf_temp, format='png')
    plt.close(fig)
    buf_temp.seek(0)
    temp_chart_base64 = base64.b64encode(buf_temp.getvalue()).decode('utf-8')

    # 2. Rainfall Comparison Plot (Bar Chart)
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=100)
    bars = ax.bar(months, monthly_rainfall, color='#2980b9', width=0.55, edgecolor='#1b4f72', alpha=0.85)

    ax.set_title(f'Monthly Rainfall Comparison: {location} ({period_str})', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Month', fontsize=11, labelpad=8)
    ax.set_ylabel('Total Rainfall (mm)', fontsize=11, labelpad=8)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    
    # Add data values on top of bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()

    buf_rain = io.BytesIO()
    plt.savefig(buf_rain, format='png')
    plt.close(fig)
    buf_rain.seek(0)
    rain_chart_base64 = base64.b64encode(buf_rain.getvalue()).decode('utf-8')

    return temp_chart_base64, rain_chart_base64
