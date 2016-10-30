#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import io
import contextlib
import traceback
import sys
import re
from sys import argv

script, PORT, token_file, sep = argv

##### set up a server
HOST = 'localhost'
PORT = int(PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket created
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
# without waiting for its natural timeout to expire.
# see: https://docs.python.org/2/library/socket.html

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + '; Message: ' + msg[1])
    quit()
s.listen(10) # Socket now listening

@contextlib.contextmanager
def stdoutIO(stdout=None):
    '''
    store outputs from stdout
    '''
    old = sys.stdout
    if stdout is None:
        stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

####### now keep talking with the client
while 1:
    ### wait to accept a connection
    conn, addr = s.accept() # Connected with  + addr[0] + str(addr[1])
    input_data = conn.recv(1024000).decode('utf-8')
    if re.sub('\s', '', input_data) == 'quit()':
        break
    ### write the codes into a file
    with open(token_file, 'w', encoding='utf-8') as f:
        f.write(input_data)
    ### print codes; execute codes
    with stdoutIO() as output:
        print(input_data)
        print(sep)
        try:
            exec(compile(open(token_file, encoding='utf-8').read(), token_file, 'exec'))
        except:
            traceback.print_exc()
    ### send output
    output_data = output.getvalue()
    conn.send(output_data.encode('utf-8'))
    conn.close()
###### clsoe & quit
conn.close()
s.shutdown(2)
s.close()
