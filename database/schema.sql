-- Weather Data Analysis System Database Schema
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
