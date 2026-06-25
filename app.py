#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs

class CalculatorHandler(BaseHTTPRequestHandler):
    def get_inputs(self, query_params):
        """Helper to safely get 'a' and 'b' from query parameters."""
        try:
            # Safely grab the first element from the query parameter lists
            a_raw = query_params.get('a', ['0'])[0]
            b_raw = query_params.get('b', ['0'])[0]
            
            a = int(a_raw) if '.' not in a_raw else float(a_raw)
            b = int(b_raw) if '.' not in b_raw else float(b_raw)
            
            return a, b, None
        except ValueError:
            return None, None, "Parameters 'a' and 'b' must be valid numbers."

    def send_json_response(self, data, status_code=200):
        """Helper to format and send JSON responses."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        # Parse the URL paths and query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Define valid routes
        valid_paths = ['/add', '/sub', '/multiply', '/divide']
        
        if path not in valid_paths:
            error_message = "Endpoint '{}' not found.".format(path)
            self.send_json_response({"error": error_message}, 404)
            return

        # Extract numeric arguments
        a, b, error = self.get_inputs(query_params)
        if error:
            self.send_json_response({"error": error}, 400)
            return

        # Perform operations based on the path
        if path == '/add':
            result = a + b
            operation = "addition"
        elif path == '/sub':
            result = a - b
            operation = "subtraction"
        elif path == '/multiply':
            result = a * b
            operation = "multiplication"
        elif path == '/divide':
            if b == 0:
                self.send_json_response({"error": "Cannot divide by zero."}, 400)
                return
            result = a / b
            operation = "division"

        # Build final JSON output to match assignment requirements
        response_data = {
            "a": a,
            "b": b,
            "operation": operation,
            "result": result
        }
        
        self.send_json_response(response_data)

def run():
    # Set to 0.0.0.0 so the server can bridge outside a Docker container
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, CalculatorHandler)
    print("Built-in server running on port 5000...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    run()

