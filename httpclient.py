#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        '''
        use the urllib.parse.urlparse to paese the URL
        and get the prot and path in the URL
        '''
        parseResult = urllib.parse.urlparse(url)

        hostname = parseResult.hostname
        port = parseResult.port

        if port == None:
            port = 80
        path = parseResult.path

        if path == '':
            path = "/"

        return hostname, port, path

    def get_ip(self, host):
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting")
            sys.exit()

        return ip

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        firstLine = data.split('\r\n')[0]
        codeStr = firstLine.split(' ')[1]
        code = int(codeStr)
        return code

    def get_headers(self,data):
        headersBody = data.partition('\r\n')[2]
        headers = headersBody.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.get_host_port(url)
        ip = self.get_ip(host)

        payload = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

        self.connect(ip, port)
        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        headers = self.get_headers(data)

        #print(body)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.get_host_port_path(url)
        ip = self.get_ip(host)
        
        payload = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-type: application/x-www-form-urlencoded\r\n"

        if args != None:
            # reference: https://stackoverflow.com/questions/40557606/how-to-url-encode-in-python-3
            # reference: https://docs.python.org/3.6/library/urllib.parse.html
            parameters = urllib.parse.urlencode(args)
            payload = payload + "Content-length: " + str(len(parameters)) + "\r\n"
            payload = payload + "Connection: close\r\n\r\n"
            payload = payload + parameters
        else:
            payload = payload + "Content-length: 0\r\nConnection: close\r\n\r\n"

        self.connect(ip, port)
        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)

        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        headers = self.get_headers(data)

        print(body)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
