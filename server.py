#  coding: utf-8 
import socketserver
from pathlib import Path
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Qian Yu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


# https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python


BUFFER_SIZE = 1024

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(BUFFER_SIZE).strip()
        if not self.data:
            return

        self.parser = {}
        self.request_methods = {
            "GET": self.do_get
        }

        requests = self.data.decode().split('\r\n')
        #for request in requests:
            #print(request)

        self.method = requests[0].split(' ')[0]
        self.source_path = requests[0].split(' ')[1]
        self.parser['method'] = self.method
        self.parser['source_path'] = 'www'+self.source_path   

        res = self.header_handler()
        self.request.sendall(res.encode(encoding='UTF-8'))

    def header_handler(self):
        method = self.parser['method']
        if(method != 'GET'):
            return self.return_header('405')
        if(not self.validation(self.parser['source_path'])):
            return self.return_header('404')

        if Path(self.parser['source_path']).is_dir():
            if(self.parser['source_path'][-1]=='/'):
                res = self.request_methods[method]()
            else:
                res = self.return_header('301',[self.source_path])
        else:
            res = self.request_methods[method]()
        return res


    def validation(self,source_path):
        if('..' in source_path.split('/') or '.' in source_path.split('/')):
            print('hahah')
            return False
            # raise Exception('Only files in ./www and deeper will be served.')
        return True

    # =============================== Get Method ===============================
    def do_get(self):
        try:
            path = self.parser['source_path'] + ('index.html' if self.parser['source_path'][-1] == '/' else '') 
            self.validation(self.parser['source_path'])
            f = open(path,'r')

            content = ''
            while True:
                text = f.read(BUFFER_SIZE)
                if not text:
                    f.close()
                    break
                content += text

            file_type = path.split('.')[-1]


            content_type_dic = {
                'html': 'Content-Type: text/html\r\n',
                'css' : 'Content-Type: text/css\r\n'
            }
            content_type = content_type_dic[file_type]
            return self.return_header('200',[content_type,content])

        except FileNotFoundError as e:
            return self.return_header('404')
    # =============================== Get Method ===============================  


    # =============================== HTTP RESPONSE STATUS CODES ===============================

    def return_header(self,status_code,args=[]):
        response_status_code = {
            '200': self.ok,
            '301': self.move_permanently,
            '404': self.not_found,
            '405': self.method_not_allowed
        }
        return response_status_code[status_code](args)

    def ok(self,args):
        header = 'HTTP/1.1 200 OK\r\n'
        content_length = 'Content-Length: ' + str(len(args[1])) + '\r\n'
        content_type = args[0]
        content = args[1]
        response = header+content_length+content_type+'\r\n'+content
        return response

    def move_permanently(self,args):
        header = 'HTTP/1.1 301 Moved Permanently\r\n'
        new_location = 'Location: '+args[0]+'/\r\n'
        response = header+new_location
        #print(res)
        return response

    def not_found(self,args):
        header = 'HTTP/1.1 404 Not Found\r\n'
        response = header
        return response

    def method_not_allowed(self,args):
        header = 'HTTP/1.1 405 Method Not Allowed\r\n'
        response = header
        return response

    # =============================== HTTP RESPONSE STATUS CODES ===============================



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True

    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
