from flask import Flask, render_template_string, request, send_from_directory, jsonify, Response
import os
import subprocess
import time
import logging
import re
import threading
from queue import Queue
from log_streamer import log_streamer_func, stream_log, summarize_logs

app = Flask(__name__)

print('app.py imported pid=', os.getpid(), 'WERKZEUG_RUN_MAIN=', os.environ.get('WERKZEUG_RUN_MAIN'))

TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), 'TestCases')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'Reports')
LOG_FILE = os.path.join(TEST_CASES_DIR, 'logfile.log')
HTML_REPORT = os.path.join(REPORTS_DIR, 'Report.html')
RUN_OUTPUT_FILE = os.path.join(REPORTS_DIR, 'console_output.txt')

# Simple in-memory pub/sub for SSE: each client gets a Queue; runner publishes lines to all queues
SUBSCRIBERS = []

def publish(line: str):
    # publish a line to all subscriber queues (non-blocking)
    for q in list(SUBSCRIBERS):
        try:
            q.put(line)
        except Exception:
            try:
                SUBSCRIBERS.remove(q)
            except Exception:
                pass

test_output = ""  # Global variable to store test output

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bookings API Testing</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden; /* prevent vertical scroll */
            color: #333;
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .container {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            padding: 24px; /* compact padding to fit viewport */
            max-width: 1100px;
            width: 100%;
            margin: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            animation: slideUp 0.8s ease-out;
        }
        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        h1 {
            text-align: center;
            color: #4a4a4a;
            margin-top: -12px; /* shift upward slightly */
            margin-bottom: 12px; /* reduce space below */
            font-size: 2em; /* slightly smaller */
            font-weight: 600; /* make bold */
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .form-row {
            display: flex;
            gap: 10px; /* slightly tighter gap between inputs */
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            margin-bottom: 6px; /* reduce vertical space between rows */
        }
        form {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 8px; /* shift rows slightly downward toward Live Log Stream */
            margin-bottom: 12px; /* tighter space below form */
            gap: 12px;
            flex-wrap: wrap;
        }
        label {
            font-weight: 500;
            color: #555;
        }
        select, button {
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 15px;
            transition: all 0.3s ease;
        }
        select {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            min-width: 220px;
        }
        /* Narrower Environment dropdown */
        #environment {
            min-width: 140px;
            width: 150px;
        }
        select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }
        #runBtn {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            margin-left: 48px; /* add horizontal tab space from Select Test Case dropdown */
        }
        #runBtn:hover:not(:disabled) {
            background: linear-gradient(45deg, #218838, #17a2b8);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
        }
        #runBtn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }
        #loader {
            display: none;
            border: 6px solid #f3f3f3;
            border-top: 6px solid #007bff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 12px auto;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        #logStreamContainer {
            display: none;
            margin-top: 16px; /* reduce gap above log stream to bring it closer to form */
            animation: fadeInUp 0.6s ease-out;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h2 {
            color: #4a4a4a;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        #logStream {
            background: white;
            color: #555;
            padding: 10px;
            border-radius: 10px;
            height: 220px; /* reduce height to avoid scroll */
            width: 100%;
            overflow-x: auto;
            overflow-y: auto;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            border: 1px solid #ddd;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .download-section {
            margin-top: 25px;
            text-align: center;
        }
        .download-btn {
            display: inline-flex;
            align-items: center;
            padding: 12px 24px;
            margin: 8px;
            background: linear-gradient(45deg, #007bff, #6610f2);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
        }
        .download-btn i {
            margin-right: 8px;
        }
        .download-btn:hover {
            background: linear-gradient(45deg, #0056b3, #5a0fc8);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
        }
        .download-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .input-field[readonly], .input-field[disabled] {
            background: #e9ecef;
            cursor: not-allowed;
            color: #666;
        }
        footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }
        @media (max-width: 600px) {
            .container {
                padding: 18px;
            }
            h1 {
                font-size: 2em;
            }
            .form-row {
                flex-direction: column;
            }
            select, button {
                width: 100%;
                min-width: unset;
            }
            #logStream {
                height: 160px;
            }
        }
        .top-bar { display:flex; justify-content: space-between; align-items:center; margin-bottom: 8px; }
        .top-bar-right { display:flex; align-items:center; gap:10px; }
        .toggle-inline label { font-weight:600; font-size: 16px; }
        .toggle-inline input[type="checkbox"] { transform: scale(1.2); }
        /* Increase height of input boxes */
        .input-field {
            height: 10px;
            padding: 12px 16px;
            font-size: 16px;
        }
        /* Reduce width specifically for BKG_TEMP input */
        #BKG_TEMP.input-field {
            width: 120px;
        }
    </style>
    <script>
        // SSE and UI helpers
        var es = null;
        var esReconnectAttempts = 0;
        var ES_MAX_RETRIES = 6;
        var linesSeen = new Set();

        function downloadConsole() {
            window.location.href = '/download/console';
        }
        function downloadLog() {
            window.location.href = '/download/log';
        }
        function downloadReport() {
            window.location.href = '/download/report';
        }
        function setDownloadVisibility(visible) {
            var display = visible ? 'inline-block' : 'none';
            document.getElementById('downloadConsole').style.display = display;
            document.getElementById('downloadLog').style.display = display;
            document.getElementById('downloadReport').style.display = display;
        }

        function setLogStreamVisibility(visible) {
            document.getElementById('logStreamContainer').style.display = visible ? 'block' : 'none';
        }

        function showError(msg) {
            var box = document.getElementById('errorBox');
            if (!box) {
                box = document.createElement('div');
                box.id = 'errorBox';
                box.style = 'background:#ffe6e6;color:#800;padding:8px;border-radius:6px;margin:10px 0;';
                var container = document.querySelector('.container');
                container.insertBefore(box, container.firstChild.nextSibling);
            }
            box.textContent = msg;
            box.style.display = 'block';
        }

        function clearError() {
            var box = document.getElementById('errorBox');
            if (box) box.style.display = 'none';
        }

        function startLoader() {
            document.getElementById('loader').style.display = 'block';
            document.getElementById('runBtn').disabled = true;
            setDownloadVisibility(false);
            clearError();
        }

        function stopLoader() {
            document.getElementById('loader').style.display = 'none';
            document.getElementById('runBtn').disabled = false;
        }

        function connectEventSource() {
            if (es) try { es.close(); } catch (e) {}
            es = new EventSource('/stream-log');
            es.onopen = function() {
                esReconnectAttempts = 0;
                console.log('SSE connected');
                stopLoader();
                setLogStreamVisibility(true);
            };
            es.onmessage = function(e) {
                var line = e.data || '';
                if (!linesSeen.has(line)) {
                    linesSeen.add(line);
                    var colored = colorizeLogLine(line);
                    var logStream = document.getElementById('logStream');
                    logStream.innerHTML += colored + "<br>";
                    logStream.scrollTop = logStream.scrollHeight;
                }
                if (line.indexOf('TEST_RUN_COMPLETE') !== -1) {
                    setDownloadVisibility(true);
                    stopLoader();
                    try { es.close(); } catch(e){}
                }
            };
            es.onerror = function(err) {
                console.error('SSE error', err);
                esReconnectAttempts += 1;
                try { es.close(); } catch(e){}
                if (esReconnectAttempts <= ES_MAX_RETRIES) {
                    var delay = Math.min(5000, 500 * esReconnectAttempts);
                    setTimeout(connectEventSource, delay);
                } else {
                    showError('Live log disconnected (no more retries).');
                    stopLoader();
                }
            };
        }

        function runTest(event) {
            event.preventDefault();
            startLoader();
            linesSeen.clear();
            document.getElementById('logStream').innerHTML = '';
            connectEventSource();
            var form = document.getElementById('testForm');
            var formData = new FormData(form);
            fetch('/run', { method: 'POST', body: formData })
            .then(function(response) {
                if (!response.ok) throw new Error('Server failed to start run');
                return response.json();
            })
            .then(function(data) {
                console.log('Run started', data);
            })
            .catch(function(err) {
                showError('Failed to start test run: ' + (err && err.message ? err.message : err));
                stopLoader();
            });
        }
        function colorizeLogLine(line) {
             if (line.includes(' INFO ')) {
                 return line.replace(' INFO ', ' <span style="color: yellow;">INFO</span> ');
             } else if (line.includes(' ERROR ')) {
                 return line.replace(' ERROR ', ' <span style="color: red;">ERROR</span> ');
             } else if (line.includes(' WARNING ')) {
                 return line.replace(' WARNING ', ' <span style="color: red;">WARNING</span> ');
             } else {
                 return line;
             }
         }
        // Set defaults based on selected test case
        document.addEventListener('DOMContentLoaded', function() {
            var testSelect = document.getElementById('test_file');
            var bkgNumInput = document.getElementById('BKG_NUM');
            var reeferInput = document.getElementById('REEFER_ID');
            var bkgTempInput = document.getElementById('BKG_TEMP');
            var envSelect = document.getElementById('environment');
            var customToggle = document.getElementById('customToggle');

            // Defensive checks: if any control is missing, do not try to operate on them
            if (!testSelect || !bkgNumInput || !reeferInput || !bkgTempInput || !envSelect || !customToggle) {
                console.warn('Form controls not fully present; skipping default population and toggle wiring.');
                return;
            }

            // Ensure custom toggle starts unchecked so defaults are applied initially
            try { customToggle.checked = false; } catch(e){/* ignore */}

            function determineDefaults() {
                var selectedTest = (testSelect.options[testSelect.selectedIndex] && testSelect.options[testSelect.selectedIndex].text) ? testSelect.options[testSelect.selectedIndex].text.trim() : '';
                var env = (envSelect && envSelect.value) ? envSelect.value.toUpperCase() : 'QA2';
                if (selectedTest.indexOf('BookingsAPI-V1') !== -1) {
                    if (env === 'INTEG') {
                        return { reefer: 'CCHD0000001,CCHD0000002', bkgNum: 'INTEGBKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG1') {
                        return { reefer: 'ZMOU8914435', bkgNum: 'ZIMINTEG1BKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG2') {
                        return { reefer: 'ZCLU9910407', bkgNum: 'ZIMINTEG2BKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'PROD') {
                        return { reefer: 'AWSA0000002,AWSA0000003', bkgNum: 'PRODBKGSAPIV1', bkgTemp: '-10' };
                    }
                    return { reefer: 'FBWS0000001,FBWS0000002', bkgNum: 'QA2BKGSAPIV1', bkgTemp: '-10' };
                } else if (selectedTest.indexOf('BookingsAPI-V2') !== -1) {
                    if (env === 'INTEG') {
                        return { reefer: 'CCHD0000003,CCHD0000004', bkgNum: 'INTEGBKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG1') {
                        return { reefer: 'ZMOU8914498', bkgNum: 'ZIMINTEG1BKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG2') {
                        return { reefer: 'ZCLU9910351', bkgNum: 'ZIMINTEG2BKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'PROD') {
                        return { reefer: 'VCVC2222221,AWSA0000001', bkgNum: 'PRODBKGSAPIV2', bkgTemp: '-10' };
                    }
                    return { reefer: 'RPLC0000001,RPLC0000002', bkgNum: 'QA2BKGSAPIV2', bkgTemp: '-10' };
                }
                return { reefer: '', bkgNum: '', bkgTemp: '' };
            }

            function setFieldDefaults(vals) {
                // Always set placeholders (safe checks)
                try { if (reeferInput) reeferInput.placeholder = vals.reefer; } catch(e){}
                try { if (bkgNumInput) bkgNumInput.placeholder = vals.bkgNum; } catch(e){}
                try { if (bkgTempInput) bkgTempInput.placeholder = vals.bkgTemp; } catch(e){}
                // Set values so they submit to backend when not custom
                if (!customToggle.checked) {
                    try { if (reeferInput) reeferInput.value = vals.reefer; } catch(e){}
                    try { if (bkgNumInput) bkgNumInput.value = vals.bkgNum; } catch(e){}
                    try { if (bkgTempInput) bkgTempInput.value = vals.bkgTemp; } catch(e){}
                }
            }

            function applyDefaults() {
                var vals = determineDefaults();
                setFieldDefaults(vals);
                // Toggle readOnly based on custom mode
                var readonly = !customToggle.checked;
                [reeferInput, bkgNumInput, bkgTempInput].forEach(function(el){ try { if (el) el.readOnly = readonly; } catch(e){} });
            }

            // Toggle behavior: enable editing when checked; restore defaults when unchecked
            customToggle.addEventListener('change', function() {
                if (!customToggle.checked) {
                    setFieldDefaults(determineDefaults());
                }
                applyDefaults();
            });
            testSelect.addEventListener('change', function(){
                if (!customToggle.checked) {
                    setFieldDefaults(determineDefaults());
                }
                applyDefaults();
            });
            if (envSelect) envSelect.addEventListener('change', function(){
                if (!customToggle.checked) {
                    setFieldDefaults(determineDefaults());
                }
                applyDefaults();
            });
            // Initial
            applyDefaults();
        });
        function summarizeLogs() {
            // Use async IIFE to allow async/await inside an inline function
            (async function() {
                try {
                    var response = await fetch('/summarize-logs');
                    if (!response.ok) {
                        var text = await response.text();
                        alert('Error summarizing logs: HTTP ' + response.status + '\\n' + text);
                        return;
                    }
                    // Try to parse JSON safely
                    var data = null;
                    try {
                        data = await response.json();
                    } catch (parseErr) {
                        var txt = await response.text();
                        alert('Error parsing summary response: ' + (parseErr && parseErr.message ? parseErr.message : parseErr) + '\\n' + txt);
                        return;
                    }
                    alert('Log Summary:\\n\\n' + (data && data.summary ? data.summary : 'No summary returned'));
                } catch (err) {
                    alert('Error summarizing logs: ' + (err && err.message ? err.message : err));
                }
            })();
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <div class="top-bar-left">
                <h1>API AUTOPILOT - OMP (BOOKINGS API)</h1>
            </div>
            <div class="top-bar-right toggle-inline">
                <input type="checkbox" id="customToggle" />
                <label for="customToggle">Use custom values</label>
            </div>
        </div>
        <form id="testForm" onsubmit="runTest(event)">
            <div class="form-row">
                <div class="input-group">
                    <label for="REEFER_ID">REEFER_ID (comma-separated):</label>
                    <input class="input-field" type="text" name="REEFER_ID" id="REEFER_ID" />
                </div>
                <div class="input-group">
                    <label for="BKG_NUM">BKG_NUM:</label>
                    <input class="input-field" type="text" name="BKG_NUM" id="BKG_NUM" />
                </div>
                <div class="input-group">
                    <label for="BKG_TEMP">BKG_TEMP:</label>
                    <input class="input-field" type="number" step="any" name="BKG_TEMP" id="BKG_TEMP" />
                </div>
            </div>
            <div class="form-row">
                <div class="input-group">
                    <label for="environment">Environment:</label>
                    <select name="environment" id="environment">
                        <option value="QA2" selected>QA2</option>
                        <option value="INTEG">INTEG</option>
                        <option value="ZIM-INTEG1">ZIM-INTEG1</option>
                        <option value="ZIM-INTEG2">ZIM-INTEG2</option>
                        <option value="PROD">PROD</option>
                    </select>
                </div>
                <div class="input-group">
                    <label for="test_file">Select Test Case:</label>
                    <select name="test_file" id="test_file">
                        {% for test_file in test_files %}
                            <option value="{{ test_file[0] }}">{{ test_file[1] }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button id="runBtn" type="submit">Run Test</button>
            </div>
        </form>
        <div id="loader"></div>
        <div id="output"></div>
        <div id="logStreamContainer" style="display:none;">
            <h2>Live Log Stream</h2>
            <pre id="logStream" style="background:#222;color:#eee;padding:10px;overflow:auto;"></pre>
            <div class="download-section">
                <button id="downloadConsole" onclick="downloadConsole()" class="download-btn"><i class="fas fa-file-download"></i> Download Console Output</button>
                <button id="downloadLog" onclick="downloadLog()" class="download-btn"><i class="fas fa-file-alt"></i> Download Log File</button>
                <button id="downloadReport" onclick="downloadReport()" class="download-btn"><i class="fas fa-file-html"></i> Download HTML Report</button>
                <button id="summarizeBtn" onclick="summarizeLogs()" class="download-btn"><i class="fas fa-brain"></i> Summarize Logs</button>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    test_files_raw = [f for f in os.listdir(TEST_CASES_DIR) if f.startswith('test_') and f.endswith('.py')]
    test_files = []
    for f in test_files_raw:
        if 'V1' in f:
            display = 'BookingsAPI-V1'
        elif 'V2' in f:
            display = 'BookingsAPI-V2'
        else:
            display = f
        test_files.append((f, display))
    return render_template_string(TEMPLATE, test_files=test_files)

@app.route('/run', methods=['POST'])
def run_test():
    test_file = request.form['test_file']
    environment = request.form.get('environment', 'QA2')
    # Export selected environment for tests
    os.environ['TEST_ENV'] = environment
    test_path = os.path.join(TEST_CASES_DIR, test_file)
    # Clear the log file before running the test
    with open(LOG_FILE, 'w'):
        pass
    cmd = [
        'pytest', '-s', test_path,
        f'--html={HTML_REPORT}',
        '--self-contained-html'
    ]
    # Prepare environment variables for subprocess, including user-specified values
    env = os.environ.copy()
    if request.form.get('REEFER_ID'):
        env['REEFER_ID'] = request.form.get('REEFER_ID')
    if request.form.get('BKG_NUM'):
        env['BKG_NUM'] = request.form.get('BKG_NUM')
    if request.form.get('BKG_TEMP'):
        env['BKG_TEMP'] = request.form.get('BKG_TEMP')
    # Ensure Python subprocesses are unbuffered for real-time streaming
    env['PYTHONUNBUFFERED'] = '1'
    # Run pytest in background thread so the Flask worker doesn't block and SSE connections stay alive
    def runner(cmd, env):
        # Run pytest and stream stdout+stderr merged to subscribers and to files
        os.makedirs(REPORTS_DIR, exist_ok=True)
        try:
            # Merge stderr into stdout for simpler streaming
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
            )
            # Open output files for write/append
            with open(RUN_OUTPUT_FILE, 'w', encoding='utf-8', errors='replace') as out_f:
                # Read line-by-line as process runs
                for raw_line in proc.stdout:
                    if raw_line is None:
                        break
                    line = raw_line.rstrip('\n')
                    # write to combined console output
                    try:
                        out_f.write(line + '\n')
                        out_f.flush();
                    except Exception:
                        pass
                # Ensure process termination
                proc.wait()
            # After completion, mark completion in log and publish final marker
            try:
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                with open(LOG_FILE, 'a', encoding='utf-8', errors='replace') as lf:
                    lf.write(f"{ts} INFO TEST_RUN_COMPLETE\n")
                publish('TEST_RUN_COMPLETE')
            except Exception:
                pass
        except Exception as e:
            # Write error info to RUN_OUTPUT_FILE and log file and notify subscribers
            try:
                with open(RUN_OUTPUT_FILE, 'w', encoding='utf-8', errors='replace') as outf:
                    outf.write(str(e) + '\n')
            except Exception:
                pass
            try:
                ts = time.strftime('%Y-%m-%d %H:%M:%S');
                with open(LOG_FILE, 'a', encoding='utf-8', errors='replace') as lf:
                    lf.write(f"{ts} ERROR Runner exception: {e}\n");
                    lf.write(f"{ts} INFO TEST_RUN_COMPLETE\n");
            except Exception:
                pass
            try:
                publish(f'ERROR Runner exception: {e}');
                publish('TEST_RUN_COMPLETE');
            except Exception:
                pass

    thread = threading.Thread(target=runner, args=(cmd, env), daemon=True)
    thread.start()
    return jsonify({'status': 'started'}), 202

@app.route('/run-result')
def run_result():
    # Return the saved console output (stdout+stderr) as JSON
    try:
        if os.path.exists(RUN_OUTPUT_FILE):
            with open(RUN_OUTPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
                data = f.read()
        else:
            data = ''
        return jsonify({'output': data})
    except Exception as e:
        return jsonify({'output': str(e)}), 500
@app.route('/download/log')
def download_log():
    # Use absolute path for directory and filename to avoid issues
    return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), 'TestCases')), 'logfile.log', as_attachment=True)

@app.route('/download/report')
def download_report():
    return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Reports')),'Report.html', as_attachment=True)

@app.route('/download/console')
def download_console():
    return send_from_directory(os.path.abspath(REPORTS_DIR), 'console_output.txt', as_attachment=True)

@app.route('/stream-log')
def stream_log_route():
    logfile_path = os.path.join(os.path.dirname(__file__), 'TestCases', 'logfile.log')
    def generate():
        last_size = 0
        while True:
            try:
                size = os.path.getsize(logfile_path)
                if size > last_size:
                    with open(logfile_path, 'r', encoding='utf-8', errors='replace') as f:
                        f.seek(last_size)
                        new_content = f.read()
                        lines = new_content.split('\n')
                        for line in lines:
                            if line.strip():
                                # Filter out unwanted log entries
                                if not re.search(r'"(POST|GET) /(run|stream-log|download/log) HTTP/1.1"', line):
                                    yield f"data: {line.strip()}\n\n"
                    last_size = size
            except OSError:
                pass
            time.sleep(0.1)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/summarize-logs', methods=['GET'])
def summarize_logs_route():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            log_content = f.read()
        if not log_content.strip():
            return jsonify({'summary': 'No logs available to summarize.'});
        summary = summarize_logs(log_content)
        return jsonify({'summary': summary});
    except Exception as e:
        return jsonify({'summary': f'Error summarizing logs: {str(e)}'}), 500
# Ensure the logger flushes logs immediately
class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()
        if hasattr(self.stream, 'fileno'):
            os.fsync(self.stream.fileno())

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/version')
def version_info():
    # Return metadata so you can confirm which file is running and its mtime
    try:
        path = os.path.abspath(__file__)
        mtime = os.path.getmtime(path)
        mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    except Exception as e:
        path = os.path.abspath(__file__)
        mtime_str = f'error: {e}'
    return jsonify({
        'path': path,
        'mtime': mtime_str,
        'pid': os.getpid(),
        'WERKZEUG_RUN_MAIN': os.environ.get('WERKZEUG_RUN_MAIN')
    })

if __name__ == '__main__':
    # Run with threaded=True and disable the reloader to avoid connection resets during dev
    app.run(debug=True, threaded=True, use_reloader=False)
