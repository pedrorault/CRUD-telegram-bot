import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = os.getenv("PORT")

class Redirect(BaseHTTPRequestHandler):
   def do_GET(self):
       self.send_response(302)
       self.send_header('Location', "t.me/BD2020EACH_Bot")
       self.end_headers()

HTTPServer(("", int(PORT)), Redirect).serve_forever()