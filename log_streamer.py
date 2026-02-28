# Fix the log_streamer_func to read logs in real-time
import os
import re
import time
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()


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


def summarize_logs(log_content):
    """
    Summarize the provided log content using OpenAI GPT-3.5-turbo.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")

    client = openai.OpenAI(api_key=api_key)

    prompt = f"Summarize the following log entries concisely:\n\n{log_content}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes log files."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"Error summarizing logs: {str(e)}"
