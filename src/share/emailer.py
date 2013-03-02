import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

ENDLESS_ADDRESS = "euquero@endlessm.com"
PASSWORD = "yesand5000"


def _create_email(name, message, recipient, file):
    # Set up header of email
    email = MIMEMultipart()
    email["From"] = "Endless Photos <photos@endlessm.com>"
    email["To"] = recipient
    if len(name.strip()) == 0:
        # All whitespace
        name = "Someone"
    email["Subject"] = name + " sent you a photo from Endless Photos!"

    # Embed image in body of email using HTML
    noreply = '<p><i>Please do not reply to this email. Replies are sent to an unmonitored inbox.</i></p>'
    body = MIMEText('<p>' + message + ' </p><img src="cid:myimage" />' + noreply, _subtype='html')
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
    except Exception:
        return False
