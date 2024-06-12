#!/usr/env python3

"""
This is a simple HTTP server that has standard GET and POST requests
implemented, so it can also receive files. A tiny utility file
request page is also implemented to facilitate adding files. (Though curl also
works).

Usage:
    Call `python3 python_rec_server.py`

Then an UNSECURE http server is running from the local directory. Access that
port via a server to easily transfer files.


## LICENSE ##

This is python_rec_server.py
Copyright © 2024 David Lowry-Duda <david@lowryduda.com>
Based on: https://gist.github.com/UniIsland/3346170

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import http.server
import socketserver
import io
import cgi
import os
import os.path


PORT = 40123


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = io.BytesIO()
        if r:
            f.write(b"Success\n")
        else:
            f.write(b"Failed\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': self.headers['Content-Type'],
                    }
            )
            print(type(form))
            try:
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        open("./%s"%record.filename, "wb").write(record.file.read())
                else:
                    open("./%s"%form["file"].filename, "wb").write(form["file"].file.read())
            except IOError:
                return (False, "Can't create file to write, do you have permission to write?")
        return (True, "Files uploaded")


submission_file_content = """<!DOCTYPE html>
<html lang="en">
  <head>
    <title>File submission</title>
    <meta charset="utf-8">
  </head>
  <body>
    <h1>Simple file submission</h1>
    <p>This is dangerous! Be careful!</p>
    <form method=post action=/ enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit>
    </form>
  </body>
</html>
"""
subfilename = "file_submission_DLD.html"


def make_submission_file():
    if not os.path.exists(subfilename):
        print(f"Creating temporary submission file {subfilename}")
        with open(subfilename, "w", encoding="utf8") as sf:
            sf.write(submission_file_content)


def clean_submission_file():
    if os.path.exists(subfilename):
        print(f"Removing temporary submission file {subfilename}")
        os.remove(subfilename)


class SubmissionFileContextManager:
    def __enter__(self):
        make_submission_file()

    def __exit__(self, exc_type, exc_value, exc_tb):
        clean_submission_file()
        if exc_type:
            print(exc_type, exc_value, exc_tb, sep="\n")


if __name__ == "__main__":
    Handler = CustomHTTPRequestHandler
    with SubmissionFileContextManager():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()
