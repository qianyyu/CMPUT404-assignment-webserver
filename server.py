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
        

        method = requests[0].split(' ')[0]
        self.parser['method'] = method
        sourcePath = requests[0].split(' ')[1]
        self.parser['sourcePath'] = './www'+sourcePath

        if method in self.avail_methods:
            if Path(self.parser['sourcePath']).is_dir():
                if(self.parser['sourcePath'][-1]=='/'):
                    res = self.avail_methods[method]()
                else:
                    res = self.return_header('301',[sourcePath])
            else:
                res = self.avail_methods[method]()
        else:
            res = self.return_header('405')

        # print ("Got a request of: %s\n" % self.data)
        self.request.sendall(res.encode(encoding='UTF-8'))


    def do_get(self):
        try:
            path = self.parser['sourcePath'] + ('index.html' if self.parser['sourcePath'][-1] == '/' else '') 

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
            print(path)
            print(content_type)
            print('\n\n\n')

            return self.return_header('200',[content_type,content])
        except Exception as e:
            #if e == FileNotFoundError:
            return self.return_header('404')
            print(e)


    def return_header(self,status_code,args=[]):
        if(status_code == '200'):
            return self.ok(args)
        if(status_code == '301'):
            return self.move_permanently(args)
        if(status_code == '404'):
            return 'HTTP/1.1 404 Not Found\r\n'
        if(status_code == '405'):
            return 'HTTP/1.1 405 Method Not Allowed\r\n'

    def move_permanently(self,args):
        header = 'HTTP/1.1 301 Moved Permanently\r\n'
        new_location = 'Location: '+args[0]+'/\r\n'
        res = header+new_location
        #print(res)
        return res

    def ok(self,args):
        header = 'HTTP/1.1 200 OK\r\n'
        contentLen = 'Content-Length: ' + str(len(args[1])) + '\r\n'
        res = header+contentLen+args[0]+'\r\n'+args[1]
        #print(res)
        return res





if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True

    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
