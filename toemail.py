import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import settings
import dbwork


def send_email(text):
    logger = logging.getLogger('App.send_email')
    db = dbwork.DataBase(settings.NAME_DATABASE)
    db.init_email_table(settings.NAME_TABLE_EMAILS)
    recipients = db.get_emails(settings.NAME_TABLE_EMAILS)
    recipients = [rec[0] for rec in recipients]

    if len(recipients) == []:
        logger.warning('List of emails is empty!')
    for recipient in recipients:
        try:
            msg = MIMEMultipart()

            msg['Subject'] = settings.SUBJECT
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = recipient

            msg.attach(MIMEText(text))

            with open('plot.png', 'rb') as f_pic:
                img = MIMEImage(f_pic.read())
                msg.attach(img)

            server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
            server.login(settings.ADMIN_EMAIL, settings.ADMIN_PASS)
            server.send_message(msg=msg, from_addr=settings.ADMIN_EMAIL, to_addrs=recipient)
            server.quit()
        except Exception as e:
            logger.info("Can't send email ")
