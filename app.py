from flask import Flask, render_template_string, request, send_from_directory, jsonify, Response, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
# Load .env early so environment variables (like GITHUB_TOKEN) are available
load_dotenv()
import subprocess
import time
import logging
import re
import threading
from queue import Queue
from log_streamer import log_streamer_func, stream_log, summarize_logs
from functools import wraps
import requests
import asyncio

print('GITHUB_TOKEN visible:', bool(os.environ.get('GITHUB_TOKEN')))

try:
    from copilot import CopilotClient, PermissionHandler
except ImportError:
    CopilotClient = None
    PermissionHandler = None

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-in-prod")

TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), 'TestCases')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'Reports')
LOG_FILE = os.path.join(TEST_CASES_DIR, 'logfile.log')
HTML_REPORT = os.path.join(REPORTS_DIR, 'Report.html')
RUN_OUTPUT_FILE = os.path.join(REPORTS_DIR, 'console_output.txt')

oauth = OAuth(app)
app.config.update({
    "AUTH0_CLIENT_ID": "UOegEOm7UJq0w22FIqMZtYYFEbDK2nJa",
    "AUTH0_CLIENT_SECRET": "lVtGjLMja0MNoBIecV2wYDR_1EZCVmkwBZMt4u0ydcZBpgxajWl1rf5i-K0MN2dz",
    "AUTH0_DOMAIN": "dev-btdohqhc48kgo2oj.us.auth0.com",
    "AUTH0_CALLBACK_URL": "http://localhost:5000/callback",
    "AUTH0_AUDIENCE": "https://dev-btdohqhc48kgo2oj.us.auth0.com/userinfo",
})

auth0 = oauth.register(
    "auth0",
    client_id=app.config["AUTH0_CLIENT_ID"],
    client_secret=app.config["AUTH0_CLIENT_SECRET"],
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration",
)


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
            overflow: auto; /* allow scrolling if content overflows */
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
        #aiLoader {
            display: none;
            border: 6px solid #f3f3f3;
            border-top: 6px solid #6610f2;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 8px auto;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
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
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        .modal {
            background: #ffffff;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }
        .modal-header {
            padding: 12px 16px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-header-left {
            flex: 1;
        }
        .modal-actions {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .modal-btn {
            background: none;
            border: none;
            color: #007bff;
            cursor: pointer;
            font-size: 14px;
            padding: 5px 10px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .modal-btn:hover {
            background-color: rgba(0, 123, 255, 0.1);
        }
        .modal-body {
            padding: 12px 16px;
            overflow-y: auto;
        }
        .modal-body pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Fira Code', 'Courier New', monospace;
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

        function startAILoader() {
            document.getElementById('aiLoader').style.display = 'block';
            document.getElementById('aiSendBtn').disabled = true;
            document.getElementById('generateTestsBtn').disabled = true;
        }

        function stopAILoader() {
            document.getElementById('aiLoader').style.display = 'none';
            document.getElementById('aiSendBtn').disabled = false;
            document.getElementById('generateTestsBtn').disabled = false;
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
                    var logStream = document.getElementById('logStream');
                    logStream.innerHTML += colorizeLogLine(line) + "<br>";
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
            
            // Temporarily enable disabled elements to include them in FormData
            var disabledElements = form.querySelectorAll('input:disabled, select:disabled');
            disabledElements.forEach(function(el) { el.disabled = false; });
            
            var formData = new FormData(form);
            
            // Re-disable elements
            disabledElements.forEach(function(el) { el.disabled = true; });
            
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
            var dryInput = document.getElementById('DRY_ID');
            var bkgTempInput = document.getElementById('BKG_TEMP');
            var envSelect = document.getElementById('environment');
            var customToggle = document.getElementById('customToggle');

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
                        return { reefer: 'CCHD0000001,CCHD0000002', dry: '', bkgNum: 'INTEGBKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG1') {
                        return { reefer: 'ZMOU8914435', dry: '', bkgNum: 'ZIMINTEG1BKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG2') {
                        return { reefer: 'ZCLU9910407', dry: '', bkgNum: 'ZIMINTEG2BKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'MATSON-INTEG') {
                        return { reefer: 'MATU5137780', dry: '', bkgNum: 'MATINTBKGSAPIV1', bkgTemp: '-10' };
                    } else if (env === 'PROD') {
                        return { reefer: 'AWSA0000002,AWSA0000003', dry: '', bkgNum: 'PRODBKGSAPIV1', bkgTemp: '-10' };
                    }
                    return { reefer: 'FBWS0000001,FBWS0000002', dry: '', bkgNum: 'QA2BKGSAPIV1', bkgTemp: '-10' };
                } else if (selectedTest.indexOf('BookingsAPI-V2') !== -1) {
                    if (env === 'INTEG') {
                        return { reefer: 'CCHD0000003,CCHD0000004', dry: '', bkgNum: 'INTEGBKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG1') {
                        return { reefer: 'ZMOU8914498', dry: '', bkgNum: 'ZIMINTEG1BKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG2') {
                        return { reefer: 'ZCLU9910351', dry: '', bkgNum: 'ZIMINTEG2BKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'MATSON-INTEG') {
                        return { reefer: 'MATU5130337', dry: '', bkgNum: 'MATINTBKGSAPIV2', bkgTemp: '-10' };
                    } else if (env === 'PROD') {
                        return { reefer: 'VCVC2222221,AWSA0000001', dry: '', bkgNum: 'PRODBKGSAPIV2', bkgTemp: '-10' };
                    }
                    return { reefer: 'RPLC0000001,RPLC0000002', dry: '', bkgNum: 'QA2BKGSAPIV2', bkgTemp: '-10' };
                } else if (selectedTest.indexOf('BookingsAPI-V3') !== -1) {
                    if (env === 'INTEG') {
                        return { reefer: 'CCHD0000003,CCHD0000004', dry: 'CCHD0000003,CCHD0000004', bkgNum: 'INTEGBKGSAPIV3', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG1') {
                        return { reefer: 'ZMOU8914498', dry: 'ZMOU8914498', bkgNum: 'ZIMINTEG1BKGSAPIV3', bkgTemp: '-10' };
                    } else if (env === 'ZIM-INTEG2') {
                        return { reefer: 'ZCLU9910351', dry: 'ZCLU9910351', bkgNum: 'ZIMINTEG2BKGSAPIV3', bkgTemp: '-10' };
                    } else if (env === 'MATSON-INTEG') {
                        return { reefer: 'MATU5130337', dry: 'MATU5130337', bkgNum: 'MATINTBKGSAPIV3', bkgTemp: '-10' };
                    } else if (env === 'PROD') {
                        return { reefer: 'VCVC2222221,AWSA0000001', dry: 'VCVC2222221,AWSA0000001', bkgNum: 'PRODBKGSAPIV3', bkgTemp: '-10' };
                    }
                    return { reefer: 'RPLC0000001', dry: 'BGFA0000001', bkgNum: 'QA2BKGSAPIV3', bkgTemp: '-10' };
                }
                return { reefer: '', dry: '', bkgNum: '', bkgTemp: '' };
            }

            function setFieldDefaults(vals) {
                // Always set placeholders (safe checks)
                try { if (reeferInput) reeferInput.placeholder = vals.reefer || ''; } catch(e){}
                try { if (dryInput) dryInput.placeholder = vals.dry || ''; } catch(e){}
                try { if (bkgNumInput) bkgNumInput.placeholder = vals.bkgNum || ''; } catch(e){}
                try { if (bkgTempInput) bkgTempInput.placeholder = vals.bkgTemp || ''; } catch(e){}
                // Set values so they submit to backend when not custom
                if (!customToggle.checked) {
                    try { if (reeferInput) reeferInput.value = vals.reefer || ''; } catch(e){}
                    try { if (dryInput) dryInput.value = vals.dry || ''; } catch(e){}
                    try { if (bkgNumInput) bkgNumInput.value = vals.bkgNum || ''; } catch(e){}
                    try { if (bkgTempInput) bkgTempInput.value = vals.bkgTemp || ''; } catch(e){}
                }
            }

            function applyDefaults() {
                var vals = determineDefaults();
                setFieldDefaults(vals);

                // Always update placeholders first so user sees expected defaults
                try { if (reeferInput) reeferInput.placeholder = vals.reefer || ''; } catch(e){}
                try { if (dryInput) dryInput.placeholder = vals.dry || ''; } catch(e){}
                try { if (bkgNumInput) bkgNumInput.placeholder = vals.bkgNum || ''; } catch(e){}
                try { if (bkgTempInput) bkgTempInput.placeholder = vals.bkgTemp || ''; } catch(e){}

                // Toggle disabled based on custom mode (defaults: disabled)
                var disableMode = !customToggle.checked;
                [reeferInput, dryInput, bkgNumInput, bkgTempInput].forEach(function(el){ try{ if(el) el.disabled = disableMode; } catch(e){} });
                
                var selectedTest = (testSelect.options[testSelect.selectedIndex] && testSelect.options[testSelect.selectedIndex].text) ? testSelect.options[testSelect.selectedIndex].text.trim() : '';
                
                // For BookingsAPI-V1 and V2: DRY_ID must be cleared and strictly disabled
                if (selectedTest.indexOf('BookingsAPI-V1') !== -1 || selectedTest.indexOf('BookingsAPI-V2') !== -1) {
                    if (dryInput) {
                        try { dryInput.value = ''; } catch(e){}
                        try { dryInput.placeholder = ''; } catch(e){}
                        try { dryInput.disabled = true; } catch(e){}
                    }
                    // Ensure REEFER_ID always reflects determineDefaults() for these versions
                    if (reeferInput) {
                        try {
                            if (!customToggle.checked) {
                                reeferInput.value = vals.reefer || '';
                            }
                        } catch(e){}
                        try { reeferInput.placeholder = vals.reefer || ''; } catch(e){}
                        try { reeferInput.disabled = disableMode; } catch(e){}
                    }
                } else if (selectedTest.indexOf('BookingsAPI-V3') !== -1) {
                    // For V3: set REEFER_ID and DRY_ID independently. Do not overwrite user input when custom mode is enabled.
                    if (reeferInput) {
                        try { if (!customToggle.checked) reeferInput.value = vals.reefer || ''; } catch(e){}
                        try { reeferInput.placeholder = vals.reefer || ''; } catch(e){}
                        try { reeferInput.disabled = disableMode; } catch(e){}
                    }
                    if (dryInput) {
                        try { if (!customToggle.checked) dryInput.value = vals.dry || ''; } catch(e){}
                        try { dryInput.placeholder = vals.dry || ''; } catch(e){}
                        try { dryInput.disabled = disableMode; } catch(e){}
                    }
                } else {
                    // Default behavior for other tests: apply placeholders/values but respect custom toggle
                    try { if (!customToggle.checked && reeferInput) reeferInput.value = vals.reefer || ''; } catch(e){}
                    try { if (!customToggle.checked && dryInput) dryInput.value = vals.dry || ''; } catch(e){}
                    try { if (!customToggle.checked && bkgNumInput) bkgNumInput.value = vals.bkgNum || ''; } catch(e){}
                    try { if (!customToggle.checked && bkgTempInput) bkgTempInput.value = vals.bkgTemp || ''; } catch(e){}
                    try { if (reeferInput) reeferInput.placeholder = vals.reefer || ''; } catch(e){}
                    try { if (dryInput) dryInput.placeholder = vals.dry || ''; } catch(e){}
                }
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

            // Show/hide local URL input based on environment selection
            document.getElementById('environment').addEventListener('change', function() {
                var localUrlGroup = document.getElementById('localUrlGroup');
                if (this.value === 'LOCAL') {
                    localUrlGroup.style.display = 'flex';
                } else {
                    localUrlGroup.style.display = 'none';
                }
            });
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

        function openModal(title, content) {
            var overlay = document.getElementById('aiModalOverlay');
            var titleEl = document.getElementById('aiModalTitle');
            var bodyEl = document.getElementById('aiModalBody');
            if (!overlay || !titleEl || !bodyEl) return;
            titleEl.textContent = title;
            bodyEl.textContent = content;
            overlay.style.display = 'flex';
        }

        function closeModal() {
            var overlay = document.getElementById('aiModalOverlay');
            if (overlay) overlay.style.display = 'none';
        }

        async function generateHumanReadableTestCases() {
             try {
                startAILoader();
                // collect user prompt from textarea and send as JSON
                var userPrompt = '';
                try { userPrompt = document.getElementById('ai_prompt') && document.getElementById('ai_prompt').value ? document.getElementById('ai_prompt').value.trim() : ''; } catch(e) { userPrompt = ''; }

                var resp = await fetch('/ai/generate-test-cases', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: userPrompt })
                });
                 if (!resp.ok) {
                     var text = await resp.text();
                     alert('Error generating test cases: HTTP ' + resp.status + '\\n' + text);
                     stopAILoader();
                     return;
                 }
                 var data;
                 try {
                     data = await resp.json();
                 } catch (e) {
                     var raw = await resp.text();
                     alert('Error parsing AI response: ' + (e && e.message ? e.message : e) + '\\n' + raw);
                     stopAILoader();
                     return;
                 }
                 var content = '';
                 if (data && data.message && data.message.content) {
                     content = data.message.content;
                 } else if (data && data.result && data.result.message && data.result.message.content) {
                     content = data.result.message.content;
                 } else if (typeof data === 'string') {
                     content = data;
                 } else {
                     content = JSON.stringify(data, null, 2);
                 }
                 openModal('AI-Response', content);
                 stopAILoader();
             } catch (err) {
                 alert('Error calling AI to generate test cases: ' + (err && err.message ? err.message : err));
                 stopAILoader();
             }
         }
         function copyToClipboard(elementId) {
            var element = document.getElementById(elementId);
            if (element) {
                navigator.clipboard.writeText(element.textContent).then(function() {
                    alert('Copied to clipboard!');
                }).catch(function(err) {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy to clipboard.');
                });
            }
        }

        function downloadAIResponse() {
            var element = document.getElementById('aiModalBody');
            if (element) {
                var content = element.textContent;
                var blob = new Blob([content], { type: 'text/plain' });
                var url = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'ai_response.txt';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        }

        // Show/hide local URL input based on environment selection
        document.getElementById('environment').addEventListener('change', function() {
            var localUrlGroup = document.getElementById('localUrlGroup');
            if (this.value === 'LOCAL') {
                localUrlGroup.style.display = 'flex';
            } else {
                localUrlGroup.style.display = 'none';
            }
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <div class="top-bar-left">
                <h1>API SENTINEL</h1>
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
                    <label for="DRY_ID">DRY_ID (comma-separated):</label>
                    <input class="input-field" type="text" name="DRY_ID" id="DRY_ID" />
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
                        <option value="LOCAL" selected>LOCAL</option>
                        <option value="QA2" selected>QA2</option>
                        <option value="INTEG">INTEG</option>
                        <option value="ZIM-INTEG1">ZIM-INTEG1</option>
                        <option value="ZIM-INTEG2">ZIM-INTEG2</option>
                        <option value="MATSON-INTEG">MATSON-INTEG</option>
                        <option value="PROD">PROD</option>
                    </select>
                </div>
                <div class="input-group" id="localUrlGroup" style="display:none;">
                    <label for="local_url">Local URL:</label>
                    <input class="input-field" type="text" name="local_url" id="local_url" placeholder="e.g., http://localhost:5000" />
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
         <div id="aiLoader"></div>
         <div id="output"></div>
         <div id="logStreamContainer" style="display:none;">
             <h2>Live Log Stream</h2>
             <pre id="logStream" style="background:#222;color:#eee;padding:10px;overflow:auto;"></pre>
             <div class="download-section">
                 <button id="downloadConsole" onclick="downloadConsole()" class="download-btn"><i class="fas fa-file-download"></i> Download Console Output</button>
                 <button id="downloadLog" onclick="downloadLog()" class="download-btn"><i class="fas fa-file-alt"></i> Download Log File</button>
                 <button id="downloadReport" onclick="downloadReport()" class="download-btn"><i class="fas fa-file-html"></i> Download Report</button>
                 <!-- <button id="summarizeBtn" onclick="summarizeLogs()" class="download-btn"><i class="fas fa-brain"></i> Summarize Logs</button> -->
                 <button id="generateTestsBtn" onclick="generateHumanReadableTestCases()" class="download-btn"><i class="fas fa-list"></i> Generate AI Test Cases</button>
             </div>
         </div>
         <!-- AI prompt always-visible section: appears even before a run starts -->
        <div id="aiPromptContainer" style="margin-top:12px; text-align:left;">
            <label for="ai_prompt" style="font-weight:600; display:block; margin-bottom:6px;">AI Prompt (optional):</label>
            <textarea id="ai_prompt" placeholder="Enter Your Prompt ..." style="width:100%; min-height:60px; padding:8px; border-radius:6px; border:1px solid #ccc; resize:vertical;"></textarea>
            <div style="margin-top:8px; text-align:right;">
                <button id="aiSendBtn" class="download-btn" onclick="generateHumanReadableTestCases()"><i class="fas fa-paper-plane"></i> Send to AI</button>
            </div>
        </div>
     </div>

     <div id="aiModalOverlay" class="modal-overlay" onclick="if(event.target===this)closeModal()">
        <div class="modal">
            <div class="modal-header">
                <div class="modal-header-left">
                    <h3 id="aiModalTitle">AI Output</h3>
                </div>
                <div class="modal-actions">
                    <button class="modal-btn" onclick="copyToClipboard('aiModalBody')">Copy to Clipboard</button>
                    <button class="modal-btn" onclick="downloadAIResponse()">Download</button>
                </div>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <pre id="aiModalBody"></pre>
            </div>
        </div>
    </div>
</body>
</html>
'''

# USERNAME = 'admin'  # Change as needed
# PASSWORD = 'password'  # Change as needed

# def check_auth(username, password):
#     return username == USERNAME and password == PASSWORD

# def authenticate():
#     return Response(
#         'Authentication required', 401,
#         {'WWW-Authenticate': 'Basic realm="Login Required"'}
#     )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri=app.config["AUTH0_CALLBACK_URL"])


@app.route("/callback")
def callback_handling():
    token = auth0.authorize_access_token()
    userinfo = token.get("userinfo") or {}
    session["user"] = {
        "sub": userinfo.get("sub"),
        "name": userinfo.get("name"),
        "email": userinfo.get("email"),
    }
    return redirect(url_for("index"))


@app.route("/logout")
@requires_auth
def logout():
    session.clear()
    return redirect(
        f"https://{app.config['AUTH0_DOMAIN']}/v2/logout?returnTo="
        f"{request.host_url.rstrip('/')}&client_id={app.config['AUTH0_CLIENT_ID']}"
    )

@app.route('/', methods=['GET'])
@requires_auth
def index():
    test_files_raw = [f for f in os.listdir(TEST_CASES_DIR) if f.startswith('test_') and f.endswith('.py')]
    test_files = []
    for f in test_files_raw:
        if 'V1' in f:
            display = 'BookingsAPI-V1'
        elif 'V2' in f:
            display = 'BookingsAPI-V2'
        elif 'V3' in f:
            display = 'BookingsAPI-V3'
        else:
            display = f
        test_files.append((f, display))
    return render_template_string(TEMPLATE, test_files=test_files)

@requires_auth
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
    env = os.environ.copy();
    if request.form.get('REEFER_ID'):
        env['REEFER_ID'] = request.form.get('REEFER_ID')
    if request.form.get('DRY_ID'):
        env['DRY_ID'] = request.form.get('DRY_ID')
    if request.form.get('BKG_NUM'):
        env['BKG_NUM'] = request.form.get('BKG_NUM')
    if request.form.get('BKG_TEMP'):
        env['BKG_TEMP'] = request.form.get('BKG_TEMP')
    # Add local URL if specified
    local_url = request.form.get('local_url')
    if environment == 'LOCAL' and local_url:
        env['TEST_SERVER_URL'] = local_url
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
    return jsonify({"status": "started"})

@requires_auth
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
@requires_auth
@app.route('/download/log')
def download_log():
    # Use absolute path for directory and filename to avoid issues
    return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), 'TestCases')), 'logfile.log', as_attachment=True)

@requires_auth
@app.route('/download/report')
def download_report():
    return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Reports')),'Report.html', as_attachment=True)

@requires_auth
@app.route('/download/console')
def download_console():
    return send_from_directory(os.path.abspath(REPORTS_DIR), 'console_output.txt', as_attachment=True)

@requires_auth
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

@requires_auth
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


async def _copilot_ask(prompt: str) -> str:
    """Send a prompt to Copilot and return the assistant content as string."""
    if CopilotClient is None:
        return "Copilot SDK (Python) is not installed. Please install the 'copilot' package."
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        return "GITHUB_TOKEN environment variable is not set."

    client = CopilotClient({
        "github_token": github_token,
        "use_logged_in_user": False,
    })

    await client.start()
    try:
        # Use PermissionHandler.approve_all only if available
        on_permission = getattr(PermissionHandler, 'approve_all', None) if PermissionHandler is not None else None
        session = await client.create_session({"model": "claude opus 4.6", "on_permission_request": on_permission})
        # Increase timeout to 120 seconds
        response = await asyncio.wait_for(session.send_and_wait({"prompt": prompt}), timeout=120.0)
        # Try to extract content safely
        try:
            content = getattr(getattr(response, 'data', None), 'content', None)
        except Exception:
            content = None
        return content if content is not None else str(response)
    finally:
        await client.stop()

@app.route('/ai/ping', methods=['GET'])
def ai_ping():
    """Health check endpoint for Copilot Python SDK."""
    try:
        result = asyncio.run(_copilot_ask("Reply with the single word: pong"))
        return jsonify({"ok": True, "copilot_reply": result}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/ai/ask', methods=['POST'])
def ai_ask():
    data = request.get_json(silent=True) or {};
    user_input = data.get('input');
    if not user_input:
        return jsonify({'error': 'Missing input'}), 400
    try:
        result = asyncio.run(_copilot_ask(user_input))
        return jsonify({'message': {'content': result}}), 200
    except Exception as e:
        return jsonify({'error': 'Copilot call failed', 'detail': str(e)}), 500

@app.route('/ai/generate-test-cases', methods=['POST'])
@requires_auth
def ai_generate_test_cases():
    """Generate human-readable test cases from the execution log.

    Accepts optional JSON body {"prompt": "..."} sent from the web UI.
    Reads LOG_FILE, prepends the optional user prompt to the instruction, sends to Copilot,
    and returns Copilot's reply under message.content.
    """
    data = request.get_json(silent=True) or {};
    user_prompt = (data.get('prompt') or '').strip();

    # Read the log file
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            log_content = f.read()
    except Exception as e:
        return jsonify({'error': 'Failed to read log file', 'detail': str(e)}), 500

    if not log_content or not log_content.strip():
        return jsonify({'error': 'Log file is empty'}), 400;

    instruction = (
        "You are an expert API test engineer.\n"
        "You are given an execution log from automated API tests.\n\n"
        "Your task is to read the log and generate HUMAN-READABLE test cases for each distinct API call.\n"
        "For each test case, produce a clear Markdown section in this format:\n\n"
        "### Test Case <number>: <short descriptive title>\n"
        "- API Endpoint: <HTTP method and path, e.g. POST /bookings/v1>\n"
        "- Purpose: <what this call is validating>\n"
        "- Pre-conditions: <any setup or assumptions>\n"
        "- Request: <high-level description of key fields, not raw JSON>\n"
        "- Expected Result: <status code and main validations>\n"
        "- Notes: <any risks, edge cases, or follow-ups>\n\n"
        "Do NOT output code. Do NOT write pytest functions.\n"
        "Focus on making the test cases easy for a human tester to understand.\n"
        "Group together log lines logically when they belong to the same API call.\n\n"
        "Below is the log content. Use it as the only source of truth.\n"
        "LOG CONTENT START\n"
    );

    if user_prompt:
        prompt = "USER PROMPT:\n" + user_prompt + "\n\n";
    else:
        prompt = instruction + log_content + "\nLOG CONTENT END\n";

    try:
        result = asyncio.run(_copilot_ask(prompt))
        return jsonify({'message': {'content': result}}), 200
    except Exception as e:
        return jsonify({'error': 'Copilot call failed', 'detail': str(e)}), 500

if __name__ == '__main__':
    # Run with threaded=True and disable the reloader to avoid connection resets during dev
    app.run(debug=True, threaded=True, use_reloader=False);
