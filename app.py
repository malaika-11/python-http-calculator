#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json


class CalculatorHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        response = json.dumps(data, indent=4).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)

    def get_numbers(self, params):
        try:
            a = float(params["a"][0])
            b = float(params["b"][0])

            # Convert whole numbers back to int for cleaner output
            if a.is_integer():
                a = int(a)
            if b.is_integer():
                b = int(b)

            return a, b

        except KeyError:
            raise ValueError("Both 'a' and 'b' parameters are required.")
        except ValueError:
            raise ValueError("'a' and 'b' must be valid numbers.")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        operations = {
            "/add": ("addition", lambda a, b: a + b),
            "/sub": ("subtraction", lambda a, b: a - b),
            "/multiply": ("multiplication", lambda a, b: a * b),
            "/divide": ("division", lambda a, b: a / b)
        }

        if path not in operations:
            self.send_json(
                {"error": f"Endpoint '{path}' not found."},
                404
            )
            return

        try:
            a, b = self.get_numbers(params)

            if path == "/divide" and b == 0:
                self.send_json(
                    {"error": "Cannot divide by zero."},
                    400
                )
                return

            operation_name, operation_func = operations[path]
            result = operation_func(a, b)

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.send_json({
                "a": a,
                "b": b,
                "operation": operation_name,
                "result": result
            })

        except ValueError as e:
            self.send_json({"error": str(e)}, 400)


def run():
    HOST = "0.0.0.0"
    PORT = 8080

    server = HTTPServer((HOST, PORT), CalculatorHandler)

    print(f"Calculator API running at http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    run()