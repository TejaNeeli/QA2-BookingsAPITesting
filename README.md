# API Automation Tool - OMP (Bookings API)

This project is an automated testing tool for the OMP Bookings API, built with Python, Flask, and Streamlit. It provides a web-based dashboard for running API tests, viewing live logs, and analyzing reports.

## Features

- **Web Dashboard (Flask)**: Interactive UI for running tests and viewing real-time execution output.
- **Analytics Dashboard (Streamlit)**: Rich dashboard for log analysis, charts, and report visualization.
- **Live Log Streaming**: Real-time log updates during test execution.
- **Security with Auth0**:
  - Flask app (`app.py`) is protected with Auth0 OIDC login.
  - Streamlit dashboard (`dashboard.py`) is protected with Auth0 login + MFA (if enabled in your tenant).
  - No credentials are stored in the app; users authenticate on Auth0’s hosted login page.
- **Test Automation**: Pytest-based test suites for V1 and V2 Bookings APIs.
- **Report Generation**: HTML reports, console output, and log downloads.
- **Multi-Environment Support**: Configurable environments (QA2, INTEG, PROD, etc.).

## Authentication Overview

Authentication is handled by [Auth0](https://auth0.com/) for both the Flask and Streamlit applications.

- The Flask app uses **Authlib**'s `flask_client` integration and enforces login via a `@requires_auth` decorator.
- The Streamlit dashboard uses **Authlib**'s `requests_client` (`OAuth2Session`) and enforces login at the top of `dashboard.py`.
- Users log in via Auth0’s hosted page (email/password and MFA if configured). After successful login, the apps receive an ID token and user info, which are stored in the session.

> **Important:** Auth0 secrets (Client Secret, etc.) must be managed securely via environment variables or a secrets manager in real deployments. Do **not** commit real secrets to source control.

## Basic Setup (Local Development)

1. **Install dependencies** (in your virtual environment):

   - Python 3.12+
   - Flask
   - Streamlit
   - Authlib
   - Pytest
   - Other libraries referenced in the code (pandas, plotly, beautifulsoup4, etc.).

2. **Configure Auth0 applications** (one tenant, at least one Regular Web App):

   - In the Auth0 Dashboard, create or use an existing Application.
   - Configure **Allowed Callback URLs** to include:
     - `http://localhost:5000/callback` (for `app.py`)
     - `http://localhost:8501/callback` (for `dashboard.py`)
   - Configure **Allowed Logout URLs** and **Allowed Web Origins** similarly if needed.
   - Note the **Domain**, **Client ID**, and **Client Secret** and configure them for your environment (e.g., via environment variables).

3. **Run the Flask app**:

   ```bash
   python app.py
   ```

   - Open `http://localhost:5000/` in a browser.
   - You will be redirected to Auth0 for login; after successful authentication you are returned to the main test runner UI.

4. **Run the Streamlit dashboard**:

   ```bash
   streamlit run dashboard.py
   ```

   - Open the URL shown in the terminal (typically `http://localhost:8501`).
   - Click **"Login with Auth0"**; complete Auth0 login (and MFA if enabled).
   - After login, you will see the analytics dashboard and your Auth0 user shown in the sidebar.

## Project Structure

```text
Api_Automation/
├── app.py                          # Main Flask application (Auth0-protected test runner)
├── dashboard.py                    # Streamlit analytics dashboard (Auth0-protected)
├── log_streamer.py                 # Log streaming utilities
├── kill_port5000.py                # Utility to kill port 5000
├── API_Requests/                   # API request classes
│   ├── V1BookingsAPIRequests.py
│   └── V2BookingsAPIRequests.py
├── TestCases/                      # Pytest test files
│   ├── test_V1BookingsAPI.py
│   ├── test_V2BookingsAPI.py
│   ├── logfile.log                 # Test logs
│   └── conftest.py                 # Pytest configuration
├── TestData/                       # Test data files
│   ├── Booking_V1.py
│   ├── Booking_V2.py
│   ├── Fleetapidata_V1.py
│   ├── Fleetapidata_V2.py
├── Reports/                        # Generated reports and console output
│   ├── Report.html
│   └── console_output.txt
├── Utilities/                      # Shared test utilities / base classes
│   ├── BaseClass_V1Bkgs.py
│   └── BaseClass_V2Bkgs.py
└── README.md
```

## Running Tests

- Tests are implemented with **pytest** under the `TestCases/` folder.
- The Flask UI (`app.py`) lets you select environment and test suite and then runs pytest in the background, streaming logs in real time.
- Generated reports and logs are written under `Reports/` and `TestCases/` and are surfaced in both the Flask UI and the Streamlit dashboard.

## Notes

- For production:
  - Move Auth0 secrets and Flask/Streamlit secrets into environment variables or a secrets manager.
  - Use HTTPS for all callback URLs.
  - Consider separating dev/test/prod Auth0 applications and tenants.
- For local testing, ensure your callback URLs and browser URLs use the **same host** (e.g., always `localhost`, not mixing `localhost` and `127.0.0.1`).
