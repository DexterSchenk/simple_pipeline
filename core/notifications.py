import re
import logging
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import utils

# todo: encrypt email.json
config = utils.load_config('email.json')


def send_email(subject, message, email_group=None, attachment=None):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config['email'], config['password'])

    msg = MIMEMultipart()
    # msg = MIMEText("""{}""".format(message))

    sender = config['email']
    recipients = config['mailing_list']['production']
    if email_group:
        recipients += config['mailing_list'][email_group]

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    msg.attach(MIMEText(message, 'plain'))

    if attachment:
        attachment_path = attachment
        filename = re.split('[\\\/]', attachment)[-1]
        attachment = open(attachment_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

    if attachment:
        has_attachment = True
    else:
        has_attachment = False
    logging.info("Sending email...")
    logging.debug("Email contents:\n"
                  "From: {frm}\n"
                  "To: {to}\n"
                  "Subject: {sub}\n"
                  "Has attachment: {attached}\n"
                  "Message:\n"
                  "{msg}".format(frm=sender, to=recipients, sub=subject, msg=message, attached=has_attachment)
    )
    server.sendmail(sender, recipients, msg.as_string())

    server.quit()


def publish_notify(name, pub_type, version, path, message, capture_path=None):
    subject = "Published {} {}-{}".format(pub_type, name, version)
    body = "Published:\n" \
           "Type:     {type}\n" \
           "Name:     {name}\n" \
           "Version:  {version}\n" \
           "Filepath: {path}\n\n" \
           "Message:\n{message}\n".format(type=pub_type, name=name, version=version, path=path, message=message)

    if pub_type == 'shot':
        email_group = 'shots'
    else:
        email_group = 'assets'

    send_email(subject, body, email_group=email_group, attachment=capture_path)
