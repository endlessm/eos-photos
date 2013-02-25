import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

ENDLESS_ADDRESS = "photos@endlessm.com"
PASSWORD = "123"

def _create_email(name, message, recipient, file):
    # Set up header of email
    email = MIMEMultipart()
    email["From"] = "Endless Photos"
    email["To"] = recipient
    email["Subject"] = name + "sent you a photo from Endless Photos!"

    # Embed image in body of email using HTML
    body = MIMEText('<p>' + message + ' </p><img src="cid:myimage" />', _subtype='html')
    email.attach(body)

    # Write image to email from file
    fp = open(file, 'rb')
    msg = MIMEImage(fp.read())
    msg.add_header('Content-Id', '<myimage>')
    #email.add_header('Content-Disposition', 'inline', filename=filename)
    email.attach(msg)
    return email.as_string()

def email_photo(name, recipient, message, filename):
    # Set up email.
    to_addr = recipient
    email = _create_email(name, message, recipient, filename)

    try:
        # For now, always using gmail server
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(ENDLESS_ADDRESS, PASSWORD)
        # Send email
        server.sendmail(ENDLESS_ADDRESS, [recipient], email)
        server.quit()
        return True
    except Exception, exception:
        return False