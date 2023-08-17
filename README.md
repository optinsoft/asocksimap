# Connect to IMAP through Socks using Python asyncio

## Installation

```bash
pip install git+https://github.com/optinsoft/asocksimap.git
```

## Usage

```python
import asyncio
from asocksimap import AsyncSocksIMAP4_SSL

def checkResponse(res, func):
    if res.result != 'OK':
        msg = reduce(lambda s, i: (s + "\n  " if i > 0 else "") + res.lines[i].decode('utf8'), range(len(res.lines)), "")
        if not msg: msg = f"{func} failed"
        raise Exception(msg) 

async def aimap_test():
    email_address = 'YOUR_ACCOUNT@hotmail.com'
    password = 'YOUR_PASSWORD'
    imap_server = 'outlook.office365.com'
    imap_port = 993
    socks_addr = '127.0.0.1'
    socks_port = 1080
    socks_type = 'socks5'

    aimap = AsyncSocksIMAP4_SSL(host=imap_server, port=imap_port, timeout=15,
                                proxy_addr=socks_addr, proxy_port=socks_port, proxy_type=socks_type)
    await aimap.wait_hello_from_server()    
    res = await aimap.login(email_address, password)
    checkResponse(res, "login")
    res = await aimap.logout()
    checkResponse(res, "logout")

loop = asyncio.get_event_loop()
loop.run_until_complete(aimap_test())

```