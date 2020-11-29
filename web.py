import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

<<<<<<< HEAD
PORT = os.getenv("PORT")
=======

>>>>>>> 1e5869f34e5dea9231a601aeb6c4a1fe755e858a

class Redirect(BaseHTTPRequestHandler):
   def do_GET(self):
       self.send_response(302)
       self.send_header('Location', "http://t.me/BD2020EACH_Bot")
       self.end_headers()

HTTPServer(("", int(PORT)), Redirect).serve_forever()