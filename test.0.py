import asyncio
import aioimaplib
from functools import reduce
import email
from email.header import decode_header
from asocksimap import AsyncSocksIMAP4, AsyncSocksIMAP4_SSL

def checkResponse(res, func, log=False):
    if log:
        for i in range(len(res.lines)):
            print(res.lines[i].decode('utf8'))
    if res.result != 'OK':
        msg = reduce(lambda s, i: (s + "\n  " if i > 0 else "") + res.lines[i].decode('utf8'), range(len(res.lines)), "")
        if not msg: msg = f"{func} failed"
        raise Exception(msg) 

async def print_inbox(aimap: aioimaplib.IMAP4, top: int = 5):
    res = await aimap.select("INBOX")
    checkResponse(res, "select")
    messages = int(res.lines[0].decode('utf8').split(' ')[0])
    print(f"messages: {messages}")
    print(f"top {top}:")
    for i in range(messages, messages-top, -1):
        if i < 1: break
        res = await aimap.fetch(str(i), "(RFC822)")
        checkResponse(res, "fetch")
        print(f"message[{i}]:")  
        if len(res.lines) >= 2:
            # parse a bytes email into a message object
            msg = email.message_from_bytes(res.lines[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]     
            if isinstance(From, bytes):
                From = From.decode(encoding)      
            print(f"Subject: {subject}")
            print(f"From: {From}")
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain":
                        # print text/plain part
                        print(body)
                    if content_type == "text/html":
                        # print text/html part
                        print(body)
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print text/plain email
                    print(body)
                if content_type == "text/html":
                    # print text/html email
                    print(body)
            print("="*100)                

async def aimap_test():
    email_address = 'YOUR_ACCOUNT@hotmail.com'
    password = 'YOUR_PASSWORD'
    imap_server = 'outlook.office365.com'
    imap_port = 993
    socks_addr = '127.0.0.1'
    socks_port = 1080
    socks_type = 'socks5'

    # aimap = aioimaplib.IMAP4(host=imap_server, port=imap_port, timeout=15)
    aimap = AsyncSocksIMAP4_SSL(host=imap_server, port=imap_port, timeout=15, proxy_addr=socks_addr, proxy_port=socks_port, proxy_type=socks_type)
    await aimap.wait_hello_from_server()    
    res = await aimap.login(email_address, password)
    checkResponse(res, "login")
    await print_inbox(aimap)
    res = await aimap.logout()
    checkResponse(res, "logout")

loop = asyncio.get_event_loop()
loop.run_until_complete(aimap_test())