import os
from flask import Flask, send_from_directory, request, jsonify
import database
import analysis

# Resolve absolute paths to frontend and data directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
DATA_DIR = os.path.join(BASE_DIR, 'data')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Initialize MySQL database and table on application launch
database.init_db()

@app.after_request
def add_cors_headers(response):
    """Allow requests from Live Server or external frontend ports."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def index():
    """Serve the main frontend dashboard."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve frontend static assets (css, js, images)."""
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """
    Handle CSV upload, validate fields, store valid records in MySQL,
    and compute monthly statistics and Matplotlib charts.
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected.'}), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'error': 'Only CSV files are supported.'}), 400

    try:
        # Validate and clean data
        valid_records, quality_report, df_valid = analysis.validate_and_clean_data(file)

        if quality_report and 'error' in quality_report:
            return jsonify({'success': False, 'error': quality_report['error']}), 400

        # Save valid records into MySQL weather_records table
        inserted_count = 0
        if valid_records:
            try:
                inserted_count = database.insert_weather_records(valid_records)
            except Exception as db_err:
                print(f"Database insertion error: {db_err}")

        # Compute monthly statistics
        summary = analysis.calculate_weather_summary(df_valid)

        # Generate Matplotlib trend and comparison plots
        temp_chart, rain_chart = analysis.generate_weather_plots(df_valid)

        return jsonify({
            'success': True,
            'quality_report': quality_report,
            'summary': summary,
            'charts': {
                'temperature': temp_chart,
                'rainfall': rain_chart
            },
            'database_inserted': inserted_count
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sample', methods=['GET'])
def load_sample():
    """Load and analyze the bundled sample weather dataset."""
    sample_path = os.path.join(DATA_DIR, 'sample_weather_data.csv')
    if not os.path.exists(sample_path):
        return jsonify({'success': False, 'error': f'Sample file not found at {sample_path}.'}), 404

    try:
        valid_records, quality_report, df_valid = analysis.validate_and_clean_data(sample_path)

        inserted_count = 0
        if valid_records:
            try:
                inserted_count = database.insert_weather_records(valid_records)
            except Exception as db_err:
                print(f"Database insertion warning: {db_err}")

        summary = analysis.calculate_weather_summary(df_valid)
        temp_chart, rain_chart = analysis.generate_weather_plots(df_valid)

        return jsonify({
            'success': True,
            'quality_report': quality_report,
            'summary': summary,
            'charts': {
                'temperature': temp_chart,
                'rainfall': rain_chart
            },
            'database_inserted': inserted_count
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/records', methods=['GET'])
def get_db_records():
    """Fetch the latest records from MySQL weather_records table."""
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Could not connect to database'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT record_id, observation_date, location, temperature, humidity, rainfall FROM weather_records ORDER BY record_id DESC LIMIT 50")
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format dates for JSON
        for r in records:
            if r.get('observation_date'):
                r['observation_date'] = str(r['observation_date'])

        return jsonify({'success': True, 'records': records})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_state():
    """
    Fetch persistent dashboard state directly from MySQL database.
    Re-computes summary and charts so the UI persists upon page refresh.
    """
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed.'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT record_id, observation_date, location, temperature, humidity, rainfall FROM weather_records ORDER BY observation_date ASC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        if not records:
            return jsonify({'success': True, 'has_data': False})

        # Build Pandas DataFrame from database rows
        import pandas as pd
        df = pd.DataFrame(records)
        df['observation_date'] = pd.to_datetime(df['observation_date'])
        df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
        df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
        df['rainfall'] = pd.to_numeric(df['rainfall'], errors='coerce')

        # Drop any nulls if present
        df_valid = df.dropna(subset=['observation_date', 'temperature', 'humidity', 'rainfall'])

        if df_valid.empty:
            return jsonify({'success': True, 'has_data': False})

        summary = analysis.calculate_weather_summary(df_valid)
        temp_chart, rain_chart = analysis.generate_weather_plots(df_valid)

        quality_report = {
            "total_records": len(df_valid),
            "valid_records": len(df_valid),
            "invalid_records": 0,
            "issues": [],
            "units": {
                "temperature": "°C (Degrees Celsius)",
                "humidity": "% (Percentage)",
                "rainfall": "mm (Millimeters)"
            }
        }

        # Format records for JSON table (newest first)
        formatted_records = []
        for r in records[::-1]:
            formatted_records.append({
                'record_id': r['record_id'],
                'observation_date': str(r['observation_date']),
                'location': r['location'],
                'temperature': r['temperature'],
                'humidity': r['humidity'],
                'rainfall': r['rainfall']
            })

        return jsonify({
            'success': True,
            'has_data': True,
            'quality_report': quality_report,
            'summary': summary,
            'charts': {
                'temperature': temp_chart,
                'rainfall': rain_chart
            },
            'records': formatted_records,
            'database_inserted': len(df_valid)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/records/purge', methods=['POST'])
def purge_records():
    """Purge all records in the weather_records table."""
    try:
        conn = database.get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed.'}), 500

        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE weather_records;")
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'All records successfully cleared from database.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=True)
