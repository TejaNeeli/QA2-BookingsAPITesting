from flask import Flask, render_template_string, request, send_from_directory, jsonify, Response
import os
import subprocess
import time
import logging
import re
import threading
from log_streamer import log_streamer_func, stream_log

app = Flask(__name__)

TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), 'TestCases')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'Reports')
LOG_FILE = os.path.join(TEST_CASES_DIR, 'logfile.log')
HTML_REPORT = os.path.join(REPORTS_DIR, 'Report.html')

test_output = ""  # Global variable to store test output

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>QA2-Bookings API Testing</title>
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
            margin-bottom: 16px;
            font-size: 2.5em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .form-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            margin-bottom: 12px;
        }
        form {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            gap: 15px;
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
            margin-top: 40px;
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
            overflow-y: auto;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            border: 1px solid #ddd;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        #logStream::-webkit-scrollbar {
            display: none;
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
    </style>
    <script>
        var es = null;
        function setDownloadVisibility(visible) {
            var display = visible ? 'inline-block' : 'none';
            document.getElementById('downloadConsole').style.display = display;
            document.getElementById('downloadLog').style.display = display;
            document.getElementById('downloadReport').style.display = display;
        }
        function setLogStreamVisibility(visible) {
            document.getElementById('logStreamContainer').style.display = visible ? 'block' : 'none';
        }
        function startLoader() {
            document.getElementById('loader').style.display = 'block';
            document.getElementById('runBtn').disabled = true;
            setDownloadVisibility(false);
        }
        function stopLoader() {
            document.getElementById('loader').style.display = 'none';
            document.getElementById('runBtn').disabled = false;
        }
        function showDownloads() {
            setDownloadVisibility(true);
        }
        function runTest(event) {
            event.preventDefault();
            startLoader();
            var form = document.getElementById('testForm');
            var formData = new FormData(form);
            document.getElementById('logStream').textContent = '';
            if (es) { es.close(); }
            es = new EventSource('/stream-log');
            var firstMessage = true;
            es.onmessage = function(e) {
                var logStream = document.getElementById('logStream');
                if (!logStream.textContent.endsWith(e.data + "\\n")) {
                    logStream.textContent += e.data + "\\n";
                    logStream.scrollTop = logStream.scrollHeight;
                    if (firstMessage) {
                        stopLoader();
                        setLogStreamVisibility(true);
                        firstMessage = false;
                    }
                }
            };
            fetch('/run', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                window.consoleOutput = data.output;
                if (es) { es.close(); }
                setDownloadVisibility(true);
            })
            .catch(() => {
                stopLoader();
                alert('Error running test case.');
            });
        }
        function downloadConsole() {
            var blob = new Blob([window.consoleOutput || ''], {type: 'text/plain'});
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'console_output.txt';
            link.click();
        }
        function downloadLog() {
            window.location.href = '/download/log';
        }
        function downloadReport() {
            window.location.href = '/download/report';
        }
        // Set defaults based on selected test case
        document.addEventListener('DOMContentLoaded', function() {
            var testSelect = document.getElementById('test_file');
            var bkgNumInput = document.getElementById('BKG_NUM');
            var reeferInput = document.getElementById('REEFER_ID');
            function applyDefaults() {
                var selectedText = testSelect.options[testSelect.selectedIndex].text;
                if (selectedText === 'QA2-V2BookingsAPI') {
                    // show defaults as placeholder (light color), keep editable
                    bkgNumInput.placeholder = 'TEJABKGSAPIV2';
                    reeferInput.placeholder = 'RPLC0000001,RPLC0000002';
                } else if (selectedText === 'QA2-V1BookingsAPI') {
                    bkgNumInput.placeholder = 'TEJABKGSAPIV1';
                    reeferInput.placeholder = 'FBWS0000001,FBWS0000002';
                } else {
                    // other: keep current placeholders
                    bkgNumInput.placeholder = bkgNumInput.placeholder || '';
                    reeferInput.placeholder = reeferInput.placeholder || '';
                }
            }
            testSelect.addEventListener('change', applyDefaults);
            applyDefaults();
        });
    </script>
</head>
<body>
    <div class="container">
        <h1>QA2-Bookings API Testing</h1>
        <form id="testForm" onsubmit="runTest(event)">
            <div class="form-row">
                <div class="input-group">
                    <label for="REEFER_ID">REEFER_ID (comma-separated):</label>
                    <input class="input-field" type="text" name="REEFER_ID" id="REEFER_ID" placeholder="FBWS0000001,FBWS0000002" />
                </div>
                <div class="input-group">
                    <label for="BKG_NUM">BKG_NUM:</label>
                    <input class="input-field" type="text" name="BKG_NUM" id="BKG_NUM" placeholder="TEJABKGSAPIV1" />
                </div>
                <div class="input-group">
                    <label for="BKG_TEMP">BKG_TEMP:</label>
                    <input class="input-field" type="number" step="any" name="BKG_TEMP" id="BKG_TEMP" placeholder="-10" />
                </div>
            </div>
            <div class="form-row">
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
            display = 'QA2-V1BookingsAPI'
        elif 'V2' in f:
            display = 'QA2-V2BookingsAPI'
        else:
            display = f
        test_files.append((f, display))
    return render_template_string(TEMPLATE, test_files=test_files)

@app.route('/run', methods=['POST'])
def run_test():
    test_file = request.form['test_file']
    test_path = os.path.join(TEST_CASES_DIR, test_file)
    # Clear the log file before running the test
    with open(LOG_FILE, 'w'):
        pass
    cmd = [
        'pytest', test_path,
        f'--log-file={LOG_FILE}',
        f'--html={HTML_REPORT}',
        '--self-contained-html',
        '--log-format=%(asctime)s %(levelname)s %(message)s',
        '--log-date-format=%Y-%m-%d %H:%M:%S'
    ]
    # Prepare environment variables for subprocess, including user-specified values
    env = os.environ.copy()
    if request.form.get('REEFER_ID'):
        env['REEFER_ID'] = request.form.get('REEFER_ID')
    if request.form.get('BKG_NUM'):
        env['BKG_NUM'] = request.form.get('BKG_NUM')
    if request.form.get('BKG_TEMP'):
        env['BKG_TEMP'] = request.form.get('BKG_TEMP')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    stdout, stderr = proc.communicate()
    output = stdout + '\n' + stderr
    return jsonify({'output': output})

@app.route('/download/log')
def download_log():
    # Use absolute path for directory and filename to avoid issues
    return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), 'TestCases')), 'logfile.log', as_attachment=True)

@app.route('/download/report')
def download_report():
    return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Reports')),'Report.html', as_attachment=True)

@app.route('/stream-log')
def stream_log_route():
    logfile_path = os.path.join(os.path.dirname(__file__), 'TestCases', 'logfile.log')
    def generate():
        with open(logfile_path, 'r', encoding='utf-8', errors='replace') as log_file:
            # First, yield all existing lines
            for line in log_file:
                if line.strip():
                    # Filter out unwanted log entries
                    if not re.search(r'"(POST|GET) /(run|stream-log|download/log) HTTP/1.1"', line):
                        yield f"data: {line.strip()}\n\n"
            # Then, continue from the end for new lines
            log_file.seek(0, os.SEEK_END)
            while True:
                line = log_file.readline()
                if line:
                    # Filter out unwanted log entries
                    if not re.search(r'"(POST|GET) /(run|stream-log|download/log) HTTP/1.1"', line):
                        yield f"data: {line.strip()}\n\n"
                else:
                    time.sleep(0.1)
    return Response(generate(), mimetype='text/event-stream')

# Ensure the logger flushes logs immediately
class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

if __name__ == '__main__':
    app.run(debug=True)