from redmail import EmailSender
import logging

logger = logging.getLogger('instaloader')

def send_mail(username, password, message, smtp_server, port, receiver):
    logger.info("Prepare mail")
    email = EmailSender(
        host=smtp_server,
        port=int(port),
        username=username,
        password=password,
        use_starttls=True
    )
    # And then you can send emails
    email.send(
        subject='Parallel Instaloader',
        sender=username,
        receivers=receiver,
        text=message
    )
    logger.info("Mail sended")

if __name__ == "__main__":
    send_mail('notifiche.fashion@yahoo.com', 'dpncsosscqollnxi', 'Provo nuovamente le notifiche', 'smtp.mail.yahoo.it', 587, ['m.mameli@pm.univpm.it', 'mameli.1.marco@gmail.com'])