"""
Root runner script for the Weather Data Analysis System.
Starts the Flask backend server from the project root.
"""
import sys
import os

# Add backend directory to Python system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Weather Data Analysis System Backend...")
    print("📍 Local URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
