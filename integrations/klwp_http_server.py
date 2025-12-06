#!/usr/bin/env python3
"""
HTTP server for KLWP CLI - accessible by any AI model via HTTP.

Usage:
  python klwp_http_server.py [--port 8080]

Endpoints:
  GET  /list
  GET  /elements?preset=name&type=TEXT
  GET  /find?preset=name&search=term
  POST /modify (JSON body: {preset, element_id, properties, save})
  POST /save (JSON body: {preset, no_backup})
  POST /reload

Examples:
  curl http://localhost:8080/list
  curl 'http://localhost:8080/elements?preset=my.klwp&type=TEXT'
  curl -X POST http://localhost:8080/modify -d '{"preset":"my.klwp","element_id":"text_1","properties":{"text":"Hello"},"save":true}'
"""

import argparse
import json
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

KLWP_CLI = Path(__file__).parent.parent / 'klwp_cli.py'


class KLWPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _execute_cli(self, args):
        """Execute KLWP CLI command."""
        cmd = ['python', str(KLWP_CLI)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = result.stdout

        return {
            'success': result.returncode == 0,
            'data': output,
            'error': result.stderr if result.stderr else None
        }

    def do_GET(self):
        """Handle GET requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # Extract single values from query params
        def get_param(name):
            values = params.get(name, [''])
            return values[0] if values else None

        if path == '/list':
            result = self._execute_cli(['list'])
            self._send_json(result)

        elif path == '/elements':
            preset = get_param('preset')
            element_type = get_param('type')

            if not preset:
                self._send_json({'error': 'Missing preset parameter'}, 400)
                return

            args = ['elements', preset, '--json']
            if element_type:
                args.extend(['--type', element_type])

            result = self._execute_cli(args)
            self._send_json(result)

        elif path == '/find':
            preset = get_param('preset')
            search = get_param('search')

            if not preset or not search:
                self._send_json({'error': 'Missing preset or search parameter'}, 400)
                return

            result = self._execute_cli(['find', preset, search, '--json'])
            self._send_json(result)

        elif path == '/':
            # API documentation
            self._send_json({
                'name': 'KLWP HTTP API',
                'version': '1.0',
                'endpoints': {
                    'GET /list': 'List all presets',
                    'GET /elements?preset=name&type=TEXT': 'List elements',
                    'GET /find?preset=name&search=term': 'Find elements',
                    'POST /modify': 'Modify element (JSON body)',
                    'POST /save': 'Save preset (JSON body)',
                    'POST /reload': 'Reload KLWP'
                }
            })

        else:
            self._send_json({'error': 'Unknown endpoint'}, 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Read JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON body'}, 400)
            return

        if path == '/modify':
            preset = data.get('preset')
            element_id = data.get('element_id')
            properties = data.get('properties', {})
            save = data.get('save', False)

            if not preset or not element_id:
                self._send_json({'error': 'Missing preset or element_id'}, 400)
                return

            args = ['modify', preset, element_id]

            if 'text' in properties:
                args.extend(['--text', properties['text']])
            if 'x' in properties:
                args.extend(['--x', str(properties['x'])])
            if 'y' in properties:
                args.extend(['--y', str(properties['y'])])
            if 'color' in properties:
                args.extend(['--color', properties['color']])

            if save:
                args.append('--save')

            result = self._execute_cli(args)
            self._send_json(result)

        elif path == '/save':
            preset = data.get('preset')
            no_backup = data.get('no_backup', False)

            if not preset:
                self._send_json({'error': 'Missing preset'}, 400)
                return

            args = ['save', preset]
            if no_backup:
                args.append('--no-backup')

            result = self._execute_cli(args)
            self._send_json(result)

        elif path == '/reload':
            result = self._execute_cli(['reload'])
            self._send_json(result)

        else:
            self._send_json({'error': 'Unknown endpoint'}, 404)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    parser = argparse.ArgumentParser(description='KLWP HTTP API Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), KLWPHandler)

    print(f"🚀 KLWP HTTP API Server")
    print(f"   Listening on http://{args.host}:{args.port}")
    print(f"\n📝 Try:")
    print(f"   curl http://{args.host}:{args.port}/list")
    print(f"   curl 'http://{args.host}:{args.port}/elements?preset=my.klwp'")
    print(f"\n   Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")


if __name__ == '__main__':
    main()
