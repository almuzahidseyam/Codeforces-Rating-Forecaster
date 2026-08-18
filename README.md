# Codeforces Rating Forecaster

A portfolio-ready Python web app that loads a Codeforces user's public rating history, visualizes the real trajectory, fits a logarithmic regression curve, and extrapolates that fitted trend across future rated contests.

> **Important:** this project visualizes and extrapolates a mathematical trend. It does **not** predict official future Codeforces ratings, participation, rank, or contest performance.

## Highlights

- Fetches public rating history from the official Codeforces API
- Works with any valid handle that has at least two rated contests
- Interactive Plotly chart for real ratings and fitted historical trend
- Adjustable 1–100 contest projection horizon
- Clear separation between actual ratings and extrapolated trend
- Current rating, peak rating, fitted trend, and projected-trend summary
- Model slope, intercept, and historical R²
- Friendly validation for invalid handles and API/network failures
- Unit tests plus GitHub Actions CI
- Streamlit-based interface that is ready for cloud deployment

## Tech stack

- **Python** — application and modelling logic
- **Streamlit** — interactive web interface
- **NumPy** — regression calculation
- **pandas** — rating-history processing
- **Plotly** — interactive visualization
- **Requests** — Codeforces API access
- **pytest** — automated tests
- **GitHub Actions** — continuous integration

## How the model works

For rated contest number `x` and Codeforces rating `y`, the app fits the historical data to:

```text
y = intercept + slope × log2(x)
```

The fitted curve is then extended to later contest numbers. Because the curve is fitted to the entire rating history, a player's latest actual rating can sit above or below the fitted trend. The projection continues from the **fitted curve**, not from the latest actual rating.

The displayed R² measures historical fit only; it is not a confidence score for future contest performance.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/almuzahidseyam/Codeforces-Rating-Forecaster.git
cd Codeforces-Rating-Forecaster
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the app

```bash
python -m streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Run the tests

Install the development dependency and run pytest:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The repository also includes a GitHub Actions workflow that runs the test suite on pushes and pull requests.

## Project structure

```text
Codeforces-Rating-Forecaster/
├── .github/
│   └── workflows/
│       └── tests.yml
├── .streamlit/
│   └── config.toml
├── src/
│   ├── __init__.py
│   ├── codeforces_api.py
│   ├── model.py
│   └── visualization.py
├── tests/
│   ├── test_codeforces_api.py
│   └── test_model.py
├── .gitattributes
├── .gitignore
├── app.py
├── CHANGELOG.md
├── LICENSE
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

## Deployment

The app is structured for deployment on Streamlit Community Cloud. After the repository is published, connect the GitHub repository in Streamlit Community Cloud and use `app.py` as the entry point.

## Roadmap

- Add a public live-demo URL and screenshot to this README
- Compare logarithmic, linear, polynomial, and recent-form models
- Add downloadable CSV/PNG output
- Add multi-handle comparison
- Add confidence/uncertainty visualization for model experiments

## Author

**Muhammad Al-Muzahid**  
GitHub: `@almuzahidseyam`

## License

Released under the [MIT License](LICENSE).
