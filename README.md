# Business Intelligence Dashboard

An interactive Python dashboard for visualizing customer transactions, revenue performance, and customer segmentation.

## Technologies

- Python
- Streamlit
- pandas
- Plotly
- pytest

## Features

- Interactive country, channel, and date filters
- Revenue and transaction KPIs
- Monthly revenue visualization
- Revenue comparison by country
- Sales channel analysis
- Customer RFM segmentation
- Customer transaction tables
- Downloadable filtered data
- Automated dashboard tests

## Dataset

The project uses a synthetic customer transaction dataset from the Customer Analytics and Segmentation project.

Only records classified as `Valid` are included in dashboard calculations.

## Running the Dashboard

Create and activate a Python virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

Launch the dashboard:

    python -m streamlit run app.py

Open the local address displayed in Terminal, usually:

    http://localhost:8501

## Testing

Run all automated tests:

    python -m pytest -q

## Sample Business Results

| Metric | Value |
|---|---:|
| Valid Transactions | 26 |
| Total Revenue | 25,180 |
| Unique Customers | 10 |
| Average Order Value | 968.46 |
| Repeat Customer Rate | 70% |

## Project Structure

    business-intelligence-dashboard/
    ├── app.py
    ├── data/
    │   └── customer_transactions.csv
    ├── tests/
    │   └── test_dashboard.py
    ├── requirements.txt
    ├── README.md
    └── .gitignore

## Author

Erick Machogu

## Disclaimer

The dataset is synthetic and intended for educational and portfolio demonstration purposes.
