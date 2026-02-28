import streamlit as st
import pandas as pd
import re
import os
import time
import io
import html as html_lib
import tempfile
from collections import Counter
from bs4 import BeautifulSoup

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
.metric-box {background:linear-gradient(90deg,var(--card-bg),#f8fbff);padding:12px;border-radius:10px;flex:1;text-align:center;color:var(--text)}
.small {font-size:0.9rem;color:var(--muted)}
.logo {font-weight:700;font-size:1.1rem;color:var(--text)}
.badge {padding:4px 8px;border-radius:8px;color:#fff;font-weight:600}
.grid-theme-light .ag-header { background: transparent; }
.grid-theme-dark .ag-root { background: #0b1220; color: #e6eef8 }
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="logo">📊 Booking Analytics Dashboard</div>', unsafe_allow_html=True)
col_title, col_spacer = st.columns([6,1])
with col_title:
    st.markdown('<div class="logo">📊 Booking Analytics Dashboard</div>', unsafe_allow_html=True)
with col_spacer:
    st.empty()

# Controls
with st.sidebar:
    st.header('Filters & Controls')
    # Theme selector and palette choices
    theme_choice = st.radio('Theme', ['Auto', 'Light', 'Dark'], index=0)
    palette_choice = st.selectbox('Color palette', ['Tight Blue', 'Muted Slate', 'Warm'], index=0)
    selected_levels = st.multiselect('Log levels', ['ERROR', 'WARNING', 'INFO'], default=['ERROR', 'WARNING', 'INFO'])
    search_text = st.text_input('Search message (substring, case-insensitive)')
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
    mcol1, mcol2, mcol3, mcol4 = st.columns([1,1,1,2])
    with mcol1:
        st.metric('Total lines', total)
    with mcol2:
        st.metric('Errors', errs)
    with mcol3:
        st.metric('Warnings', warns)
    with mcol4:
        st.markdown('<div class="small">Log level distribution</div>', unsafe_allow_html=True)
        st.bar_chart(df['level'].value_counts())
    st.markdown('</div>', unsafe_allow_html=True)

    # Timestamps are parsed in parse_log; ensure we have a datetime index for time charts
    if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df_time = df.set_index('timestamp')
    else:
        df_time = df.copy()

    # Display a pageable subset to avoid huge render times
    st.write('### Log entries')
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
        # JS renderer for severity badges
        badge_renderer = JsCode("""
        function(params) {
            var level = params.value || '';
            var color = '#6c757d';
            if (level === 'ERROR') color = '#dc3545';
            else if (level === 'WARNING') color = '#fd7e14';
            else if (level === 'INFO') color = '#20c997';
            var span = document.createElement('span');
            span.textContent = level;
            span.style.padding = '4px 8px';
            span.style.borderRadius = '8px';
            span.style.color = '#fff';
            span.style.background = color;
            span.style.fontWeight = '600';
            return span.outerHTML;
        }
        """)

        # Configure severity/level column to show badge and make timestamp sortable
        if 'level' in df_display.columns:
            gb.configure_column('level', header_name='Severity', cellRenderer=badge_renderer, filter='agSetColumnFilter')
        if 'timestamp' in df_display.columns:
            gb.configure_column('timestamp', header_name='Timestamp', type=['dateColumnFilter','customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm:ss')

        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum')
        grid_options = gb.build()

        AgGrid(
            df_display,
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
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
        st.download_button('Download CSV', data=csv_bytes, file_name='log_export.csv', mime='text/csv')
        if excel_bytes is not None:
            st.download_button('Download Excel', data=excel_bytes, file_name='log_export.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.markdown('<div class="small">Excel export available if <code>openpyxl</code> is installed.</div>', unsafe_allow_html=True)
        st.download_button('Download full logfile', data=log_contents, file_name='logfile.log', mime='text/plain')
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

    # Pie chart and bar chart for log levels
    if not df.empty and 'level' in df.columns:
        level_counts = df['level'].value_counts()
        st.write('#### Log Level Distribution (Pie Chart)')
        st.plotly_chart({
            'data': [{
                'labels': level_counts.index.tolist(),
                'values': level_counts.values.tolist(),
                'type': 'pie',
                'hole': .3
            }],
            'layout': {'title': 'Log Level Pie Chart'}
        })
        st.write('#### Log Level Distribution (Bar Chart)')
        st.bar_chart(level_counts)

# Read Console Output and Report HTML
console_output = ''
if os.path.exists(CONSOLE_OUTPUT_FILE):
    with open(CONSOLE_OUTPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
        console_output = f.read()

report_html = ''
if os.path.exists(REPORT_HTML_FILE):
    with open(REPORT_HTML_FILE, 'r', encoding='utf-8', errors='replace') as f:
        report_html = f.read()

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

# Add tabs for Log File, Console Output, and Report HTML
log_tab, console_tab, report_tab = st.tabs(["Log File", "Console Output", "Report.html"])

with log_tab:
    # Refresh behavior (manual + best-effort auto)
    def _attempt_rerun():
        # Prefer the public API
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
            return
        # Try internal RerunException for older/newer Streamlit builds
        try:
            from streamlit.runtime.scriptrunner.script_runner import RerunException
            raise RerunException()
        except Exception:
            # Clear caches where possible to allow next render to pick up changes
            try:
                clear_cache = getattr(st, 'cache_data', None)
                clear_fn = getattr(clear_cache, 'clear', None)
                if callable(clear_fn):
                    clear_fn()
            except Exception:
                pass
            try:
                singleton_container = getattr(st, 'experimental_singleton', None)
                if singleton_container is not None:
                    clear_method = getattr(singleton_container, 'clear', None)
                    if callable(clear_method):
                        clear_method()
                    else:
                        # Some Streamlit builds might not expose a clear method; try alternative locations
                        alt = getattr(st, 'experimental_memo', None)
                        alt_clear = getattr(alt, 'clear', None) if alt is not None else None
                        if callable(alt_clear):
                            alt_clear()
            except Exception:
                pass
            # Final fallback: ask user to reload
            st.info('Please reload the page to refresh the dashboard.')

    if refresh:
        _attempt_rerun()

    if auto_refresh:
        time.sleep(refresh_interval)
        _attempt_rerun()

with console_tab:
    st.subheader("Console Output")
    if console_output:
        st.code(console_output, language='text')
        # Pie and bar chart for console output levels
        c_counts = parse_console_output(console_output)
        if c_counts:
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
        else:
            st.info('No key levels found in console output.')
    else:
        st.info("No console output found.")

with report_tab:
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
