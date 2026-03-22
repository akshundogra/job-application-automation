#!/usr/bin/env python3
"""
webhook_server.py — Local HTTP server for n8n to trigger job application script
Run this once: python3 webhook_server.py
Then n8n calls http://host.docker.internal:5001/run
"""

from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

PYTHON_PATH = '/Users/YOUR_USERNAME/anaconda3/bin/python3'
SCRIPT_PATH = '/Users/YOUR_USERNAME/.n8n-files/apply_changes.py'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/run', methods=['POST'])
def run_script():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON body received'}), 400

        # Determine config path based on language
        language = data.get('language', 'English Only')
        if 'English' in language:
            config_path = '/Users/YOUR_USERNAME/.n8n-files/config_en.json'
        else:
            config_path = '/Users/YOUR_USERNAME/.n8n-files/config_de.json'

        # Write the config file
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Run the Python script
        result = subprocess.run(
            [PYTHON_PATH, SCRIPT_PATH, config_path],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            return jsonify({
                'error': result.stderr,
                'stdout': result.stdout
            }), 500

        # Parse the JSON output from the script
        output_lines = result.stdout.strip().split('\n')
        last_line = output_lines[-1]
        output = json.loads(last_line)

        return jsonify({
            'success': True,
            'files': output,
            'log': result.stdout
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script timed out after 2 minutes'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Job Application Webhook Server starting...")
    print("   Listening on http://0.0.0.0:5001")
    print("   n8n should call: http://host.docker.internal:5001/run")
    print("   Health check: http://localhost:5001/health")
    print("   Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5001, debug=False)
