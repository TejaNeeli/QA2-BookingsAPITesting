import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import os
import pandas as pd
import re
import time
import io
import html as html_lib
import tempfile
from collections import Counter
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


# Auth0 configuration
AUTH0_DOMAIN = "dev-btdohqhc48kgo2oj.us.auth0.com"
AUTH0_CLIENT_ID = "UOegEOm7UJq0w22FIqMZtYYFEbDK2nJa"
AUTH0_CLIENT_SECRET = "lVtGjLMja0MNoBIecV2wYDR_1EZCVmkwBZMt4u0ydcZBpgxajWl1rf5i-K0MN2dz"
AUTH0_CALLBACK_URL = "http://localhost:8501/callback"
AUTH0_SCOPE = "openid profile email"

# Initialize session state variables
if "auth0_token" not in st.session_state:
    st.session_state["auth0_token"] = None
if "auth0_user" not in st.session_state:
    st.session_state["auth0_user"] = None

# Function to create Auth0 client
def get_auth0_client():
    return OAuth2Session(
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        scope=AUTH0_SCOPE,
        redirect_uri=AUTH0_CALLBACK_URL,
    )

# Generate Auth0 login URL
def login_url():
    client = get_auth0_client()
    authorization_endpoint = f"https://{AUTH0_DOMAIN}/authorize"
    uri, state = client.create_authorization_url(authorization_endpoint)
    # Keep state in session if needed later, but we won't manually compare it
    st.session_state["auth0_state"] = state
    return uri

# Handle Auth0 callback and fetch token/userinfo
def handle_callback():
    query_params = st.query_params
    code = query_params.get("code")
    if not code:
        return False

    client = get_auth0_client()
    token_endpoint = f"https://{AUTH0_DOMAIN}/oauth/token"

    # Let Authlib handle state/CSRF validation internally when exchanging the code
    token = client.fetch_token(
        token_endpoint,
        code=code,
        grant_type="authorization_code",
    )
    st.session_state["auth0_token"] = token

    # Fetch userinfo
    user_client = OAuth2Session(
        client_id=AUTH0_CLIENT_ID,
        token=token,
    )
    userinfo = user_client.get(f"https://{AUTH0_DOMAIN}/userinfo").json()
    st.session_state["auth0_user"] = userinfo

    # Clear query params so reloads don't re-run callback
    try:
        st.query_params.clear()
    except Exception:
        pass

    return True

# Ensure user is logged in
def ensure_logged_in():
    if st.session_state.get("auth0_user"):
        return True

    # If we just came back from Auth0 with a code, finish login
    if handle_callback():
        return True

    # Not logged in yet: show a real button
    auth_url = login_url()
    if st.button("Login with Auth0"):
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={auth_url}" />',
            unsafe_allow_html=True,
        )
    st.stop()

# Call ensure_logged_in() to enforce login
ensure_logged_in()
user = st.session_state.get("auth0_user", {})
st.sidebar.write(f"Logged in as: {user.get('name') or user.get('email')}")

# --- Existing dashboard code starts here ---

# Detect optional AG Grid support and import symbols for static analysis
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, JsCode  # type: ignore
    AGGRID_AVAILABLE = True
except Exception:
    AgGrid = None
    GridOptionsBuilder = None
    JsCode = None
    AGGRID_AVAILABLE = False

LOG_FILE = os.path.join(os.path.dirname(__file__), 'TestCases', 'logfile.log')
# Paths for additional files
CONSOLE_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'Reports', 'console_output.txt')
REPORT_HTML_FILE = os.path.join(os.path.dirname(__file__), 'Reports', 'Report.html')

# Safe default so download button has a defined variable on all code paths
log_contents = ''


@st.cache_data(ttl=5)  # Cache data for 5 seconds to make refresh more responsive
def parse_log():
    data = []
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()
    with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
        allowed = {'ERROR', 'WARNING', 'INFO', 'DEBUG'}
        for line in f:
            # Try to capture timestamp, level token, and the remainder message.
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+([A-Z]+)\s+(.*)', line)
            if match:
                timestamp, level_token, message = match.groups()
                level = (level_token or '').strip().upper()
                # Normalize known levels; fall back to scanning the message for keywords
                if level not in allowed:
                    found = None
                    for kw in ('ERROR', 'WARNING', 'INFO', 'DEBUG'):
                        if re.search(r'\b' + kw + r'\b', message, flags=re.IGNORECASE):
                            found = kw
                            break
                    level = found if found is not None else 'OTHER'
                message = (message or '').strip()
                data.append({'timestamp': timestamp, 'level': level, 'message': message})
            else:
                # Line didn't match expected format: try loose parsing
                # Attempt to extract timestamp and classify by keywords
                ts_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                timestamp = ts_match.group(1) if ts_match else ''
                message = line.strip()
                level = 'OTHER'
                for kw in ('ERROR', 'WARNING', 'INFO', 'DEBUG'):
                    if re.search(r'\b' + kw + r'\b', line, flags=re.IGNORECASE):
                        level = kw
                        break
                data.append({'timestamp': timestamp, 'level': level, 'message': message})
    df = pd.DataFrame(data)
    # Parse timestamps to datetime for sorting and charts; tolerate parsing failures
    if not df.empty:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        except Exception:
            pass
        # ensure level column exists
        if 'level' in df.columns:
            df['level'] = df['level'].astype(str)
    return df


st.set_page_config(page_title='Booking Analytics Dashboard', layout='wide', page_icon='📊')
# Base CSS uses variables so we can switch palettes/themes dynamically
st.markdown("""
<style>
:root {
  --bg: #f6f9ff;
  --page-bg: linear-gradient(135deg,#ffffff,#f6f9ff);
  --card-bg: #ffffff;
  --card-border: rgba(0,0,0,0.04);
  --text: #0f172a;
  --muted: #6b7280;
  --accent: #2563eb;
  --error: #dc2626;
  --warning: #f97316;
  --info: #10b981;
}
.stApp .main .block-container{padding-top:0.5rem;padding-bottom:0.5rem;background:var(--page-bg)}
.card {background: linear-gradient(135deg,var(--card-bg), #f6f9ff);border-radius:12px;padding:12px;margin-bottom:12px;border:1px solid var(--card-border);color:var(--text)}
.metrics {display:flex;gap:12px}
.metric-box {background:linear-gradient(90deg,var(--card-bg),#f8fbff);padding:12px;border-radius:10px;border:1px solid var(--card-border);flex:1;text-align:center;color:var(--text)}
.small {font-size:0.9rem;color:var(--muted)}
.logo {font-weight:700;font-size:2rem;color:var(--text);margin-top:-10px;}
.badge {padding:4px 8px;border-radius:8px;color:#fff;font-weight:600}
.grid-theme-light .ag-header { background: transparent; }
.grid-theme-dark .ag-root { background: #0b1220; color: #e6eef8 }
.plotly-graph-div:hover { cursor: pointer !important; }
.plotly-graph-div svg:hover { cursor: pointer !important; }
</style>
""", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; margin-bottom: 10px; background: var(--page-bg);"><div class="logo">📊 Booking Analytics Dashboard</div></div>', unsafe_allow_html=True)

# Initialize selected view
if "selected_view" not in st.session_state:
    st.session_state.selected_view = "Log File"

# Initialize metric filter
if "metric_filter" not in st.session_state:
    st.session_state.metric_filter = None

# Reset logic: clear filters and selections if reset flag is set
if 'reset_all' in st.session_state:
    st.session_state.metric_filter = None
    st.session_state.selected_levels = ['ERROR', 'WARNING', 'INFO']
    st.session_state.search_text = ''
    st.session_state['last_pie_click'] = None
    st.session_state['last_bar_click'] = None
    st.session_state['chart_version'] = st.session_state.get('chart_version', 0) + 1
    del st.session_state['reset_all']
    st.rerun()

# Buttons for navigation
# col1, col2, col3 = st.columns([1,1,1])
# with col1:
#     if st.button("Log File", key="log_file_btn"):
#         st.session_state.selected_view = "Log File"
# with col2:
#     if st.button("Console Output", key="console_output_btn"):
#         st.session_state.selected_view = "Console Output"
# with col3:
#     if st.button("Report.html", key="report_html_btn"):
#         st.session_state.selected_view = "Report.html"

selected_view = st.session_state.selected_view

# Controls
with st.sidebar:
    st.header('Filters & Controls')
    # Theme selector and palette choices
    theme_choice = st.radio('Theme', ['Auto', 'Light', 'Dark'], index=0)
    palette_choice = st.selectbox('Color palette', ['Tight Blue', 'Muted Slate', 'Warm'], index=0)
    selected_levels = st.multiselect('Log levels', ['ERROR', 'WARNING', 'INFO'], default=['ERROR', 'WARNING', 'INFO'], key='selected_levels')
    search_text = st.text_input('Search message (substring, case-insensitive)', key='search_text')
    max_rows = st.number_input('Max rows to show', min_value=10, max_value=2000, value=500, step=10)
    refresh = st.button('Refresh')
    auto_refresh = st.checkbox('Auto-refresh', value=False)
    refresh_interval = st.slider('Auto-refresh interval (seconds)', min_value=2, max_value=60, value=5)
    st.markdown('---')
    st.markdown('Data source: <code>TestCases/logfile.log</code>', unsafe_allow_html=True)
    if not AGGRID_AVAILABLE:
        st.info("Optional: install interactive grid for better table UX: pip install streamlit-aggrid")

# Inject theme CSS based on selection
def _inject_theme_css(theme_choice, palette_choice):
    # Dark detection
    dark = False
    if theme_choice == 'Dark' or (theme_choice == 'Auto' and st.get_option('theme.base') == 'dark'):
        dark = True

    if dark:
        # Use darker palettes
        if palette_choice == 'Warm':
            page = 'linear-gradient(135deg,#2b0f05,#35120a)'
            card_bg = '#1b1210'
            text = '#fff2e8'
            muted = '#d7c1ad'
            accent = '#ff9f43'
        elif palette_choice == 'Muted Slate':
            page = 'linear-gradient(135deg,#0b1220,#071226)'
            card_bg = '#071026'
            text = '#e6eef8'
            muted = '#9aa8c7'
            accent = '#475569'
        else:
            page = 'linear-gradient(135deg,#07102a,#08112f)'
            card_bg = '#07102a'
            text = '#e6eef8'
            muted = '#9aa8c7'
            accent = '#2563eb'
        css = f"""
        <style>
        :root {{ --page-bg: {page}; --card-bg: {card_bg}; --card-border: rgba(255,255,255,0.06); --text: {text}; --muted: {muted}; --accent: {accent}; }}
        .grid-theme-dark .ag-root {{ background: #07102a; color: var(--text) }}
        </style>
        """
    else:
        # Light palettes
        if palette_choice == 'Warm':
            page = 'linear-gradient(135deg,#fffaf0,#fff5ec)'
            card_bg = '#fffaf0'
            text = '#0f172a'
            muted = '#6b7280'
            accent = '#b45309'
        elif palette_choice == 'Muted Slate':
            page = 'linear-gradient(135deg,#fbfdff,#f4f7fb)'
            card_bg = '#fbfdff'
            text = '#0f172a'
            muted = '#6b7280'
            accent = '#475569'
        else:
            page = 'linear-gradient(135deg,#ffffff,#f6f9ff)'
            card_bg = '#ffffff'
            text = '#0f172a'
            muted = '#6b7280'
            accent = '#2563eb'
        css = f"""
        <style>
        :root {{ --page-bg: {page}; --card-bg: {card_bg}; --card-border: rgba(0,0,0,0.04); --text: {text}; --muted: {muted}; --accent: {accent}; }}
        .grid-theme-light .ag-header {{ background: transparent; }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# apply theme immediately
_inject_theme_css(theme_choice, palette_choice)

# Refresh behavior (manual + best-effort auto)
def _attempt_rerun():
    st.rerun()

if refresh:
    st.session_state['reset_all'] = True
    _attempt_rerun()

if auto_refresh:
    time.sleep(refresh_interval)
    _attempt_rerun()

if selected_view == "Log File":
    # Read and display logs
    try:
        df = parse_log()
    except Exception as e:
        st.error(f'Failed to read log file: {e}')
        st.stop()

    if not os.path.exists(LOG_FILE):
        st.warning('Log file not found: ' + LOG_FILE)
        st.stop()

    # Show last modified timestamp
    try:
        mtime = os.path.getmtime(LOG_FILE)
        st.sidebar.write('Last updated:', pd.to_datetime(mtime, unit='s'))
    except Exception:
        pass

    if df.empty:
        st.info('No log data found.')
    else:
        # Compute full level counts for charts (before filtering)
        full_level_counts = df['level'].value_counts() if 'level' in df.columns else pd.Series()
        # Ensure INFO, ERROR, WARNING are always displayed
        for level in ['INFO', 'ERROR', 'WARNING']:
            if level not in full_level_counts:
                full_level_counts[level] = 0

        # Filtering
        if selected_levels:
            df = df[df['level'].isin(selected_levels)]
        if search_text:
            df = df[df['message'].str.contains(re.escape(search_text), case=False, na=False)]

        # Summary metrics with compact cards
        total = int(df.shape[0])
        errs = int(df['level'].eq('ERROR').sum()) if 'level' in df.columns else 0
        warns = int(df['level'].eq('WARNING').sum()) if 'level' in df.columns else 0
        infos = int(df['level'].eq('INFO').sum()) if 'level' in df.columns else 0
        st.markdown('<div class="card">', unsafe_allow_html=True)
        mcol1, mcol2, mcol3, mcol4 = st.columns([1,1,1,1])
        with mcol1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric('Total Lines', total)
            st.markdown('</div>', unsafe_allow_html=True)
        with mcol2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric('Info', infos)
            st.markdown('</div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric('Errors', errs)
            st.markdown('</div>', unsafe_allow_html=True)
        with mcol4:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric('Warnings', warns)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Use metrics values for charts to match
        level_counts = pd.Series({'INFO': infos, 'ERROR': errs, 'WARNING': warns})
        # Define colors for each level
        level_colors = {'ERROR': 'red', 'WARNING': 'orange', 'INFO': 'green'}

        # Layout: Left column for charts, right for table and downloads
        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.write('#### Log Level Distribution (Pie Chart)')
            # Pie chart and bar chart for log levels (using metrics values)
            # Filter level_counts for pie chart to only include levels with counts > 0
            filtered_level_counts = level_counts[level_counts > 0]
            pie_labels = list(filtered_level_counts.index)
            pie_values = list(filtered_level_counts.values)
            marker_colors = [level_colors.get(label, 'gray') for label in pie_labels]
            fig_pie = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, hole=0.3)])
            fig_pie.update_traces(marker=dict(colors=marker_colors))
            fig_pie.update_layout(hovermode='closest', clickmode='event+select', width=400)
            pie_selected = plotly_events(fig_pie, click_event=True, select_event=False, key=f'pie_chart_{st.session_state.get("chart_version", 0)}')
            if pie_selected and pie_selected != st.session_state.get('last_pie_click'):
                point_number = pie_selected[0].get('pointNumber')
                if point_number is not None and point_number < len(pie_labels):
                    label = pie_labels[point_number]
                    st.session_state.metric_filter = label
                    st.session_state['last_pie_click'] = pie_selected
                    st.rerun()

            st.write('#### Log Level Distribution (Bar Chart)')
            filtered_level_counts_bar = level_counts[level_counts > 0]
            marker_colors_bar = [level_colors.get(x, 'gray') for x in filtered_level_counts_bar.index]
            fig_bar = go.Figure(data=[go.Bar(x=list(filtered_level_counts_bar.index), y=list(filtered_level_counts_bar.values))])
            fig_bar.update_traces(marker_color=marker_colors_bar)
            fig_bar.update_layout(hovermode='closest', clickmode='event+select', width=400)
            bar_selected = plotly_events(fig_bar, click_event=True, select_event=False, key=f'bar_chart_{st.session_state.get("chart_version", 0)}')
            if bar_selected and bar_selected != st.session_state.get('last_bar_click'):
                label = bar_selected[0].get('x')
                if label:
                    st.session_state.metric_filter = label
                    st.session_state['last_bar_click'] = bar_selected
                    st.rerun()



        with col_right:
            # Apply metric filter
            if st.session_state.metric_filter:
                df = df[df['level'] == st.session_state.metric_filter]

            # Timestamps are parsed in parse_log; ensure we have a datetime index for time charts
            if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df_time = df.set_index('timestamp')
            else:
                df_time = df.copy()

            # Display a pageable subset to avoid huge render times
            st.write('### Log entries')
            if st.button("Refresh", key="grid_refresh"):
                st.session_state['reset_all'] = True
                st.rerun()
            # Add a severity badge column for non-AG Grid fallback too
            def make_badge(level):
                if level == 'ERROR':
                    return 'ERROR'
                if level == 'WARNING':
                    return 'WARNING'
                return 'INFO'

            df_display = df.sort_values(by='timestamp', ascending=False).head(int(max_rows)).copy()

            # Read full logfile contents for the "Download full logfile" button (safe fallback)
            try:
                with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                    log_contents = f.read()
            except Exception:
                log_contents = ''

            # Prepare download bytes (CSV + Excel if possible)
            csv_bytes = df_display.to_csv(index=False).encode('utf-8')
            excel_bytes = None
            try:
                # Write Excel to a temporary file to avoid BytesIO type warnings and
                # to make large exports safer on memory-constrained environments.
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    tmp_name = tmp.name
                with pd.ExcelWriter(tmp_name, engine='openpyxl') as writer:
                    df_display.to_excel(writer, index=False, sheet_name='logs')
                with open(tmp_name, 'rb') as f:
                    excel_bytes = f.read()
                try:
                    os.remove(tmp_name)
                except Exception:
                    pass
            except Exception:
                excel_bytes = None

            # Render with AG Grid if available, otherwise fallback to an HTML-colored table
            if AGGRID_AVAILABLE:
                gb = GridOptionsBuilder.from_dataframe(df_display)
                # Configure severity/level column as plain text so users see INFO/ERROR/WARNING
                if 'level' in df_display.columns:
                    gb.configure_column('level', header_name='Severity', filter='agSetColumnFilter')
                if 'timestamp' in df_display.columns:
                    gb.configure_column('timestamp', header_name='Timestamp', type=['dateColumnFilter','customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm:ss')

                gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
                gb.configure_default_column(groupable=False, value=True, enableRowGroup=False, aggFunc='sum', filter=False)
                grid_options = gb.build()

                AgGrid(
                    df_display,
                    gridOptions=grid_options,
                    enable_enterprise_modules=False,
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=False,
                    theme='light'
                )
            else:
                # Build an HTML table with colored rows by severity for better readability
                colors = {'ERROR': '#fdecea', 'WARNING': '#fff4e5', 'INFO': '#e9f7ef', 'OTHER': '#f0f0f0'}
                table_html = ['<div style="overflow:auto;max-height:600px;"><table style="width:100%;border-collapse:collapse;font-family:monospace;">']
                # header
                table_html.append('<thead><tr>')
                for col in df_display.columns:
                    table_html.append(f'<th style="text-align:left;padding:6px;border-bottom:1px solid #ddd;">{html_lib.escape(str(col))}</th>')
                table_html.append('</tr></thead>')
                # body
                table_html.append('<tbody>')
                for _, row in df_display.iterrows():
                    level = str(row.get('level', ''))
                    bg = colors.get(level, 'transparent')
                    table_html.append(f'<tr style="background:{bg};">')
                    for col in df_display.columns:
                        cell = row[col]
                        cell_text = html_lib.escape(str(cell))
                        table_html.append(f'<td style="padding:6px;border-bottom:1px solid #f0f0f0;vertical-align:top;">{cell_text}</td>')
                    table_html.append('</tr>')
                table_html.append('</tbody></table></div>')
                st.markdown(''.join(table_html), unsafe_allow_html=True)

            # Provide download buttons (CSV always; Excel if available) and small time-series charts
            c1, c2 = st.columns([3,2])
            with c1:
                col_csv, col_log = st.columns(2)
                with col_csv:
                    st.download_button('Download CSV', data=csv_bytes, file_name='log_export.csv', mime='text/csv')
                with col_log:
                    st.download_button('Download full logfile', data=log_contents, file_name='logfile.log', mime='text/plain')
                if excel_bytes is not None:
                    st.download_button('Download Excel', data=excel_bytes, file_name='log_export.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            with c2:
                # Plot errors over time if timestamps available
                try:
                    if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                        errs_ts = df[df['level'] == 'ERROR'].set_index('timestamp').resample('1h').size()
                        warns_ts = df[df['level'] == 'WARNING'].set_index('timestamp').resample('1h').size()
                        combined = pd.DataFrame({'Errors': errs_ts, 'Warnings': warns_ts}).fillna(0)
                        if not combined.empty:
                            st.area_chart(combined)
                except Exception:
                    pass

# --- Helper functions for parsing key points ---

def parse_console_output(text):
    # Count occurrences of ERROR, WARNING, INFO (case-insensitive)
    levels = ['ERROR', 'WARNING', 'INFO']
    counter = Counter()
    for line in text.splitlines():
        for level in levels:
            if level in line.upper():
                counter[level] += 1
    return counter

def parse_report_html(html_text):
    # Try to extract pass/fail/error counts from HTML tables or summary blocks
    soup = BeautifulSoup(html_text, 'html.parser')
    counter = Counter()
    # Example: look for table cells or spans with keywords
    for tag in soup.find_all(text=True):
        txt = tag.strip().upper()
        if 'PASS' in txt:
            counter['PASS'] += 1
        if 'FAIL' in txt:
            counter['FAIL'] += 1
        if 'ERROR' in txt:
            counter['ERROR'] += 1
        if 'WARNING' in txt:
            counter['WARNING'] += 1
    return counter

# Read Console Output and Report HTML

console_output = ''

if os.path.exists(CONSOLE_OUTPUT_FILE):
    with open(CONSOLE_OUTPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
        console_output = f.read()
report_html = ''
if os.path.exists(REPORT_HTML_FILE):
    with open(REPORT_HTML_FILE, 'r', encoding='utf-8', errors='replace') as f:
        report_html = f.read()

elif selected_view == "Console Output":
    st.subheader("Console Output")
    if console_output:
        # Parse severity counts from console output
        c_counts = parse_console_output(console_output)
        if c_counts:
            # Build a small DataFrame of console lines with inferred severity
            console_lines = []
            for line in console_output.splitlines():
                level = None
                upper = line.upper()
                if "ERROR" in upper:
                    level = "ERROR"
                elif "WARNING" in upper:
                    level = "WARNING"
                elif "INFO" in upper:
                    level = "INFO"
                if level:
                    console_lines.append({"level": level, "raw": line})
            console_df = pd.DataFrame(console_lines) if console_lines else pd.DataFrame(columns=["level", "raw"])

            # Let user choose which level to inspect (simulates clicking on chart segment)
            levels_available = list(c_counts.keys())
            selected_level = st.selectbox(
                "Select a severity level to view details",
                options=levels_available,
                index=0 if levels_available else None,
            ) if levels_available else None

            # Show charts
            st.write('#### Console Output Level Distribution (Pie Chart)')
            st.plotly_chart({
                'data': [{
                    'labels': list(c_counts.keys()),
                    'values': list(c_counts.values()),
                    'type': 'pie',
                    'hole': .3
                }],
                'layout': {'title': 'Console Output Pie Chart'}
            })

            st.write('#### Console Output Level Distribution (Bar Chart)')
            st.bar_chart(pd.Series(c_counts))

            # Helper to strip common logger prefixes and show only the actual message
            def _extract_message(raw_line: str) -> str:
                text = raw_line
                # Drop leading "INFO - " / "ERROR - " / "WARNING - " patterns
                text = re.sub(r"^(INFO|ERROR|WARNING)\s*-\s*", "", text, flags=re.IGNORECASE)
                # Drop typical logger preamble like "self.logger.info("API Request: POST ...")"
                text = re.sub(r"^self\.logger\.[a-zA-Z_]+\(f?\"", "", text)
                text = re.sub(r"\"\)$", "", text)
                return text.strip()

            # Show filtered records for the selected level
            if selected_level and not console_df.empty:
                st.write(f"#### Console records for: {selected_level}")
                filtered = console_df[console_df['level'] == selected_level]

                # 1) Cleaned log text (actual log messages without logger syntax)
                messages = [
                    _extract_message(raw)
                    for raw in filtered['raw'].tolist()
                    if _extract_message(raw)
                ]
                if messages:
                    st.code("\n".join(messages), language="text")
                else:
                    st.info("No console messages found for the selected level.")

                # 2) Keep table with raw lines for reference
                st.dataframe(filtered.rename(columns={"raw": "line"}), width='content')
            elif console_df.empty:
                st.info('No classified console records found.')
        else:
            st.info('No key levels found in console output.')
    else:
        st.info("No console output found.")

elif selected_view == "Report.html":
    st.subheader("Report.html")
    if report_html:
        st.components.v1.html(report_html, height=600, scrolling=True)
        # Pie and bar chart for report summary
        r_counts = parse_report_html(report_html)
        if r_counts:
            st.write('#### Report Summary Distribution (Pie Chart)')
            st.plotly_chart({
                'data': [{
                    'labels': list(r_counts.keys()),
                    'values': list(r_counts.values()),
                    'type': 'pie',
                    'hole': .3
                }],
                    'layout': {'title': 'Report Summary Pie Chart'}
                })
            st.write('#### Report Summary Distribution (Bar Chart)')
            st.bar_chart(pd.Series(r_counts))
        else:
            st.info('No summary keywords found in report.')
    else:
        st.info("No report HTML found.")
