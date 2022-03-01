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


def safe_send(conn, msg):
    print(msg)
    msg_len = len(msg)
    totalsent = 0
    while totalsent < msg_len:
        sent = conn.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent += sent


def send_to_server(from_client, to_server):
    schedule_close = False
    ip6 = re.compile(f'\\[[^]]*]:{port}')
    msg = from_client.recv(2048)

    if len(msg) == 0:
        safe_send(to_server, msg)
        from_client.close()
        sel.unregister(from_client)
        schedule_close = True

    msg = str(msg, 'ISO-8859-1', 'ignore')

    ipm = ip6.search(msg)
    msg = msg.replace(msg[ipm.start():ipm.end()], f'127.0.0.1:{port}')
    msg = msg.encode('ISO-8859-1')

    safe_send(to_server, msg)
    if schedule_close:
        to_server.close()
        sel.unregister(to_server)


def send_to_client(to_client, from_server):
    eor = re.compile('\\r\\n\\r\\n\\Z')
    msg = from_server.recv(2048)

    eorm = eor.search(str(msg, 'ISO-8859-1', 'ignore'))
    if eorm or len(msg) == 0:
        safe_send(to_client, msg)
        to_client.close()
        from_server.close()
        sel.unregister(to_client)
        sel.unregister(from_server)
        return

    safe_send(to_client, msg)


def accept_connection(sock):
    client, addr = sock.accept()
    client.setblocking(False)
    server = socket.create_connection(("127.0.0.1", port))
    server.setblocking(False)
    sel.register(client, selectors.EVENT_READ, (send_to_server, client, server))
    sel.register(server, selectors.EVENT_READ, (send_to_client, client, server))


def clear_screen():
    os.system('cls')
    print('Simple Reverse IPv6 to IPv4 TCP proxy\nVersion 1.0')
    print('-' * 100)


def main():
    global sel
    global port
    addr = None
    clear_screen()

    try:
        config_file = open('config.txt', 'rb')
        addr = pickle.loads(config_file.read())
        config_file.close()
    except FileNotFoundError:
        pass
    except EOFError:
        addr = None
    if not addr:
        port = input("Which port do you want? (Default: 7245)\nEnter: ")
        if port:
            port = int(port)
        else:
            port = 7245
        addrs = socket.getaddrinfo(socket.gethostname(), port, family=socket.AF_INET6)
        valid_addrs = []
        for addr in addrs:
            if not addr[4][0].startswith('fe80'):
                valid_addrs.append(addr)

        if len(valid_addrs) > 1:
            print("Please select which address to bind to:")
            for addr in valid_addrs:
                print(f"[{valid_addrs.index(addr) + 1}] {addr[4][0]}")
            selection = int(input("Enter: ")) - 1
            addr = valid_addrs[selection][4][:2]
        else:
            addr = valid_addrs[0][4][:2]

        if input('Do you want to safe config for next time?(Y/N)\nEnter: ') == 'Y':
            config_file = open('config.txt', 'wb')
            config_file.write(pickle.dumps(addr))
            config_file.close()

        clear_screen()

    print(f"Reverse Proxy is up and running on [{addr[0]}] with port {addr[1]}")

    sel = selectors.DefaultSelector()
    ipv6side = socket.create_server(addr, family=socket.AF_INET6, backlog=20)
    ipv6side.setblocking(False)
    sel.register(ipv6side, selectors.EVENT_READ, accept_connection)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            if isinstance(callback, tuple):
                callback[0](callback[1], callback[2])
            else:
                callback(key.fileobj)


if __name__ == '__main__':
    main()
