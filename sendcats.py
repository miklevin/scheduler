import PIL
import glob
import smtplib
import requests
import imagehash
from os import remove
from time import sleep
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from email import encoders
from art import text2art as fig
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from sqlitedict import SqliteDict as sqldict
from email.mime.multipart import MIMEMultipart


# Create the plain-text email
msg_text = '''Dear You,

This is a plain text email where the line returns are preserved
like this.

Mike Levin'''

# Create the HTML email
msg_html = '''<html><head></head><body><h1>Dear You,</h1>
<p>This is an HTML email where we don't have to worry about line
returns because html will make its own line wrap decisions.</p>
<h3>Mike Levin</h3><img src="cid:image" /></body></html>'''

with open('mail_from.txt') as fh:
    email, paswd = [x.strip() for x in fh.readlines()]

with open('mail_to.txt') as fh:
    mail_to = [x.strip() for x in fh.readlines()]

server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login(email, paswd)

msgdict = MIMEMultipart()
msgdict.preamble = 'This is a multi-part message in MIME format.'
msgdict['From'] = email
msgdict['To'] = ', '.join([x for x in mail_to])
msgdict['Subject'] = "HTML Test Email"

# Create plain text and HTML alternatives
msg_alts = MIMEMultipart('alternative')
msgdict.attach(msg_alts)
msg_alts.attach(MIMEText(msg_text))
msg_alts.attach(MIMEText(msg_html, 'html'))

with open("mike-levin-logo.png", 'rb') as fh:
    msg_img = MIMEImage(fh.read())
    msg_img.add_header('Content-Disposition', 'inline', filename='Mike Levin')

msgdict.add_header('Content-ID', '<image>')
msgdict.attach(msg_img)

# Fetch files from Web and make Zip
files = glob.glob('./cats/*')
for file in files:
    remove(file)
try:
    remove('cats.zip')
except OSError:
    pass

p = Path("./cats/").mkdir(exist_ok=True)

for i in range(1, 4):
    resp = requests.get('https://thiscatdoesnotexist.com/')
    filebinary = resp.content
    readytohash = PIL.Image.open(BytesIO(filebinary))
    aphash = imagehash.phash(readytohash)
    filename = f'{aphash}.jpg'
    with open(f"./cats/{filename}", 'wb') as fh:
        fh.write(filebinary)
        with sqldict('/home/ubuntu/data/cats.db') as db:
            db[str(aphash)] = filebinary
            db.commit()
    sleep(3)

files = glob.glob('./cats/*')
with ZipFile('cats.zip', 'w') as zfh:
    for file in files:
        zfh.write(file)

mimecats = MIMEBase('application', 'octet-stream')
with open(Path('cats.zip'), 'br') as zfh:
    mimecats.set_payload(zfh.read())
encoders.encode_base64(mimecats)
mimecats.add_header('Content-Disposition', "attachment; filename=cats.zip")
msgdict.attach(mimecats)

try:
    server.sendmail(email, mail_to, msgdict.as_string())
    print(fig('Email Sent!'))
except:
    print('error sending mail')

server.quit()
