# AI Trader

AI Trader is an automated system that monitors financial news and executes trades based on sentiment analysis. It is built to run continuously while providing a clear interface for tracking performance.

The system is fully built in Python, using Streamlit for the user interface.

## Quick Start

To run the project locally, follow these steps:

1. Install dependencies:
   pip install -r requirements.txt

2. Run the trading engine:
   python -m src.main

3. Launch the dashboard:
   streamlit run streamlit_app.py

## Streamlit Cloud Deployment

This project is designed to be easily deployed to Streamlit Community Cloud.

Point the Streamlit deployment settings to 'streamlit_app.py' as the main entry point. The application will automatically pick up your configuration and data files.

## Project Features

- Real-time news ingestion and automated sentiment scoring.
- S&P 500 stock selection and analysis.
- Web dashboard for monitoring cash, open positions, and system health.
- Built-in emergency stop and risk management controls.
- Professional light-mode design optimized for clarity.

## Technical Details

The application is structured into a backend engine ('src/main.py') and a Streamlit frontend ('streamlit_app.py'). They communicate via shared state files in the 'data' directory, allowing for a decoupled and reliable architecture suitable for 24/7 operation.
