# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content('Hello')

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'The content'
msg['From'] = 'tech@daiteco.ru'
msg['To'] = 'a-egorov@inbox.ru, alexey19820211@gmail.com, alex19820211@yandex.ru'

# Send the message via our own SMTP server.
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()

print ("OK .. {}".format(msg['To']))
