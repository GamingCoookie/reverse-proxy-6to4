"""
Copyright 2022 GamingCoookie

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import socket
import re
import selectors
import os
import pickle
from threading import Thread


def safe_send(conn, msg):
    print(msg)
    msg_len = len(msg)
    totalsent = 0
    while totalsent < msg_len:
        sent = conn.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent += sent


def clear_screen():
    os.system('cls')
    print('Simple Reverse IPv6 to IPv4 TCP proxy\nVersion 1.0')
    print('-' * 100)


class ReverseProxy(Thread):
    def __init__(self, addr: str = None, port: int = None, standalone: bool = False):
        self.addr = (addr, port) if addr is not None else None
        self.port = port
        self.standalone = standalone
        self.sel = None

        Thread.__init__(self, name=f'{addr=} {port=}')

    def accept_connection(self, sock):
        client, addr = sock.accept()
        client.setblocking(False)
        server = socket.create_connection(("127.0.0.1", self.port))
        server.setblocking(False)
        self.sel.register(client, selectors.EVENT_READ, (self.send_to_server, client, server))
        self.sel.register(server, selectors.EVENT_READ, (self.send_to_client, client, server))

    def run(self):
        if self.standalone:
            clear_screen()
            try:
                config_file = open('config.txt', 'rb')
                self.addr = pickle.loads(config_file.read())
                config_file.close()
            except FileNotFoundError:
                pass
            except EOFError:
                self.addr = None
            if not self.addr:
                self.port = input("Which port do you want? (Default: 7245)\nEnter: ")
                if self.port:
                    self.port = int(self.port)
                else:
                    self.port = 7245
                addrs = socket.getaddrinfo(socket.gethostname(), self.port, family=socket.AF_INET6)
                valid_addrs = []
                for addr in addrs:
                    if not addr[4][0].startswith('fe80'):
                        valid_addrs.append(addr)

                if len(valid_addrs) > 1:
                    print("Please select which address to bind to:")
                    for addr in valid_addrs:
                        print(f"[{valid_addrs.index(addr) + 1}] {addr[4][0]}")
                    selection = int(input("Enter: ")) - 1
                    self.addr = valid_addrs[selection][4][:2]
                else:
                    self.addr = valid_addrs[0][4][:2]

                if input('Do you want to safe config for next time?(Y/N)\nEnter: ') == 'Y':
                    config_file = open('config.txt', 'wb')
                    config_file.write(pickle.dumps(self.addr))
                    config_file.close()

                    clear_screen()

            print(f"Reverse Proxy is up and running on [{self.addr[0]}] with port {self.addr[1]}")

        self.sel = selectors.DefaultSelector()
        ipv6side = socket.create_server(self.addr, family=socket.AF_INET6, backlog=20)
        ipv6side.setblocking(False)
        self.sel.register(ipv6side, selectors.EVENT_READ, self.accept_connection)

        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                if isinstance(callback, tuple):
                    callback[0](callback[1], callback[2])
                else:
                    callback(key.fileobj)

    def send_to_client(self, to_client, from_server):
        eor = re.compile('\\r\\n\\r\\n\\Z')
        msg = from_server.recv(2048)

        eorm = eor.search(str(msg, 'ISO-8859-1', 'ignore'))
        if eorm or len(msg) == 0:
            safe_send(to_client, msg)
            to_client.close()
            from_server.close()
            self.sel.unregister(to_client)
            self.sel.unregister(from_server)
            return

        safe_send(to_client, msg)

    def send_to_server(self, from_client, to_server):
        ip6 = re.compile(f'\\[[^]]*]:{self.port}')
        msg = from_client.recv(2048)

        ipm = ip6.search(str(msg, 'ISO-8859-1', 'ignore'))
        if ipm:
            msg = str(msg, 'ISO-8859-1', 'ignore')
            msg = msg.replace(msg[ipm.start():ipm.end()], f'127.0.0.1:{self.port}')
            msg = msg.encode('ISO-8859-1')

        if len(msg) == 0:
            safe_send(to_server, msg)
            to_server.close()
            from_client.close()
            self.sel.unregister(from_client)
            self.sel.unregister(to_server)
            return

        safe_send(to_server, msg)


if __name__ == '__main__':
    p = ReverseProxy(standalone=True)
    p.start()
    p.join()
