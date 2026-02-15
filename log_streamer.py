# Fix the log_streamer_func to read logs in real-time
import os
import re
import time
from datetime import datetime


def log_streamer_func(logfile_path):
    def generate():
        # Open with encoding and replace errors to avoid crashes on bad bytes
        with open(logfile_path, 'r', encoding='utf-8', errors='replace') as f:
            f.seek(0)
            buffer = ''
            while True:
                chunk = f.readline()
                if chunk:
                    buffer += chunk
                    # If we have at least one complete line, yield them
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        # yield complete line (without the newline)
                        yield f'data: {line.rstrip()}\n\n'
                else:
                    # Handle file truncation
                    current_pos = f.tell()
                    f.seek(0, os.SEEK_END)
                    end_pos = f.tell()
                    if end_pos < current_pos:
                        f.seek(0)
                        buffer = ''
                    time.sleep(0.1)
    return generate


def stream_log(logfile_path):
    def generate():
        with open(logfile_path, 'r', encoding='utf-8', errors='replace') as log_file:
            log_file.seek(0, os.SEEK_END)  # Start at the end of the file
            while True:
                line = log_file.readline()
                if line:
                    # Filter out unwanted log entries
                    if not re.search(r'"(POST|GET) /(run|stream-log|download/log) HTTP/1.1"', line):
                        # Ensure consistent timestamps
                        if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}', line):
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            line = f'{timestamp} {line}'
                        yield f'data: {line.rstrip()}\n\n'
                else:
                    # Handle file truncation
                    current_pos = log_file.tell()
                    log_file.seek(0, os.SEEK_END)
                    if log_file.tell() < current_pos:
                        log_file.seek(0)
                    time.sleep(0.1)  # Wait briefly before checking for new lines
    return generate
