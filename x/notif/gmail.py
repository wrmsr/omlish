"""
def _main():
    cfg = load_secrets()
    sender_email = cfg['gmail_sender_email']
    password = cfg['gmail_sender_password']

    smtp_server = 'smtp.gmail.com'
    port = 587  # For starttls

    receiver_email = cfg['gmail_receiver_email']

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    server = smtplib.SMTP(smtp_server, port)

    try:
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email, 'hi')

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()
"""

"""
https://sendgrid.com/marketing/sendgrid-services-cro/#compare-plans ?

Incoming Mail (IMAP) Server
imap.gmail.com
Requires SSL: Yes
Port: 993

Outgoing Mail (SMTP) Server
smtp.gmail.com
Requires SSL: Yes
Requires TLS: Yes (if available)
Requires Authentication: Yes
Port for SSL: 465
Port for TLS/STARTTLS: 587

Full Name or Display Name	Your name
Account Name, User name, or Email address	Your full email address
Password	Your Gmail password

https://realpython.com/python-send-email
https://support.google.com/mail/thread/23341254?hl=en

2-step + app pw
OAuth
"""
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from omserv.secrets import load_secrets


cfg = load_secrets()

sender_email = cfg['gmail_sender_email']
sender_password = cfg['gmail_sender_app_password']
receiver_email = cfg['gmail_receiver_email']


def send_simple(server):
    server.sendmail(sender_email, receiver_email, 'hi')


def send_fancy(server):
    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""
    html = """\
    <html>
      <body>
        <p>Hi,<br>
           How are you?<br>
           <a href="http://www.realpython.com">Real Python</a> 
           has many great tutorials.
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )


def send_attachment(server):
    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = __file__

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(filename)}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    server.sendmail(sender_email, receiver_email, text)


def main():
    smtp_server = 'smtp.gmail.com'
    port = 587  # For starttls

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    server = smtplib.SMTP(smtp_server, port)

    try:
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, sender_password)

        # send_simple(server)
        # send_fancy(server)
        send_attachment(server)

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()


if __name__ == '__main__':
    main()
