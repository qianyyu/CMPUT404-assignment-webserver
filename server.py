#  coding: utf-8 
import socketserver
from pathlib import Path
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

'''
        parser['method'] = method
        parser['sourcePath'] = sourcePath

'''
# https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python


BUFFER_SIZE = 1024

class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(BUFFER_SIZE).strip()
        self.parser = {}
        self.avail_methods = {
            "GET": self.do_get
        }

        requests = self.data.decode().split('\r\n')


        for request in requests:
            print(request)
        print('\n\n\n')

        method = requests[0].split(' ')[0]
        self.parser['method'] = method
        sourcePath = requests[0].split(' ')[1]
        self.parser['sourcePath'] = './www'+sourcePath

        if method in self.avail_methods:
            if Path(self.parser['sourcePath']).is_dir():
                if(self.parser['sourcePath'][-1]=='/'):
                    res = self.avail_methods[method]()
                else:
                    res = self.return_header('301')+'Location: '+sourcePath+'/\r\n'
            else:
                res = self.avail_methods[method]()
        else:
            res = self.return_res('405')

        # print ("Got a request of: %s\n" % self.data)
        self.request.sendall(res.encode(encoding='UTF-8'))

    def do_get(self):
        try:
            path = self.parser['sourcePath'] + 'index.html' if self.parser['sourcePath'][-1] == '/' else self.parser['sourcePath']

            #if('../' in os.path.relpath(path,'./')):
             #   raise FileNotFoundError
            f = open(path,'r')
            content = ''
            while True:
                text = f.read(BUFFER_SIZE)
                if not text:
                    f.close()
                    break
                content += text
            file_type = path.split('.')[-1]
            return self.return_res('200',file_type,content)
        except Exception as e:
            #if e == FileNotFoundError:
            return self.return_res('404')
            print(e)

    def return_res(self,status_code='200',file_type = 'html',content=''):

        content_type_dic = {
            'html': 'Content-Type: text/html; charset=utf-8\r\n',
            'css' : 'Content-Type: text/css; charset=utf-8\r\n'
        }

        header = self.return_header(status_code)

        contentLen = 'Content-Length: ' + str(len(content)) + '\r\n'

        return header+contentLen+content_type_dic[file_type]+content



    def return_header(self,status_code='200'):
        header_dic = {
            '200': 'HTTP/1.1 200 OK\r\n',
            '301': 'HTTP/1.1 301 Moved Permanently',
            '404': 'HTTP/1.1 404 Not Found\r\n',
            '405': 'HTTP/1.1 405 Method Not Allowed\r\n',
            
        }

        return header_dic[status_code]



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True

    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
