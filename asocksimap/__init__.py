#
#    asocksimap : Connect to IMAP through Socks using Python asyncio
#    Copyright (c) 2023 Vitaly (Optinsoft)
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.

import asyncio
from aioimaplib import IMAP4ClientProtocol, IMAP4, IMAP4_PORT, IMAP4_SSL_PORT
from typing import Callable, Optional
import ssl
import sys
from aiosocks import Socks4Addr, Socks5Addr, Socks4Auth, Socks5Auth, Socks4Protocol, Socks5Protocol

PY37_OR_LATER = sys.version_info[:2] >= (3, 7)

def get_running_loop() -> asyncio.AbstractEventLoop:
    if PY37_OR_LATER:
        return asyncio.get_running_loop()
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        raise RuntimeError("no running event loop")
    return loop

PROXY_TYPE_SOCKS4 = SOCKS4 = 1
PROXY_TYPE_SOCKS5 = SOCKS5 = 2

class AsyncSocksIMAP4(IMAP4):
    
    SOCKS_PROXY_TYPES = {"socks4": PROXY_TYPE_SOCKS4, "socks5": PROXY_TYPE_SOCKS5}

    TIMEOUT_SECONDS = 10.0

    def __init__(self, host: str = '127.0.0.1', port: int = IMAP4_PORT, loop: asyncio.AbstractEventLoop = None,
                 timeout: float = TIMEOUT_SECONDS, conn_lost_cb: Callable[[Optional[Exception]], None] = None,
                 ssl_context: ssl.SSLContext = None,
                 proxy_addr=None, proxy_port=None, rdns=True, 
                 username=None, password=None, proxy_type=None):

        self.proxy_addr = proxy_addr
        self.proxy_port = proxy_port
        self.rdns = rdns
        self.username = username
        self.password = password
        self.proxy_type = AsyncSocksIMAP4.SOCKS_PROXY_TYPES[proxy_type.lower()] if not proxy_type is None else None

        IMAP4.__init__(self, host, port, loop, timeout, conn_lost_cb, ssl_context)
    
    def create_client(self, host: str, port: int, loop: asyncio.AbstractEventLoop,
                      conn_lost_cb: Callable[[Optional[Exception]], None] = None, ssl_context: ssl.SSLContext = None) -> None:
        local_loop = loop if loop is not None else get_running_loop()
        self.protocol = IMAP4ClientProtocol(local_loop, conn_lost_cb)
        
        if self.proxy_type == PROXY_TYPE_SOCKS4:
            proxy = Socks4Addr(self.proxy_addr, self.proxy_port)
            proxy_auth = Socks4Auth(self.username) if self.username != None else None
        elif self.proxy_type == PROXY_TYPE_SOCKS5:
            proxy = Socks5Addr(self.proxy_addr, self.proxy_port)
            proxy_auth = Socks5Auth(self.username, self.password) if self.username != None else None
        else:
            local_loop.create_task(local_loop.create_connection(lambda: self.protocol, host, port, ssl=ssl_context))
            return

        dst = (host, port)
        waiter = asyncio.Future(loop=local_loop)
        remote_resolve = self.rdns
        server_hostname = dst[0] if ssl_context else None

        def socks_factory():
            if isinstance(proxy, Socks4Addr):
                socks_proto = Socks4Protocol
            else:
                socks_proto = Socks5Protocol
            return socks_proto(proxy=proxy, proxy_auth=proxy_auth, dst=dst,
                            app_protocol_factory=lambda: self.protocol,
                            waiter=waiter, remote_resolve=remote_resolve,
                            loop=local_loop, ssl=ssl_context, server_hostname=server_hostname)
        
        local_loop.create_task(local_loop.create_connection(
            socks_factory, proxy.host, proxy.port))

class AsyncSocksIMAP4_SSL(AsyncSocksIMAP4):
    def __init__(self, host: str = '127.0.0.1', port: int = IMAP4_SSL_PORT, loop: asyncio.AbstractEventLoop = None,
                 timeout: float = IMAP4.TIMEOUT_SECONDS, ssl_context: ssl.SSLContext = None,
                 proxy_addr=None, proxy_port=None, rdns=True, 
                 username=None, password=None, proxy_type=None):
        super().__init__(host, port, loop, timeout, None, ssl_context,
                         proxy_addr, proxy_port, rdns, 
                         username, password, proxy_type)

    def create_client(self, host: str, port: int, loop: asyncio.AbstractEventLoop,
                      conn_lost_cb: Callable[[Optional[Exception]], None] = None, ssl_context: ssl.SSLContext = None) -> None:
        if ssl_context is None:
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        super().create_client(host, port, loop, conn_lost_cb, ssl_context)

