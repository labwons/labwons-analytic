from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP


class Mail(MIMEMultipart):
    """
    e-mail 전송 서비스
    """

    def __init__(self):
        super().__init__()
        self['From'] = 'snob.labwons@gmail.com'
        self.content = ""
        return

    @property
    def Subject(self) -> str:
        return self['Subject']

    @Subject.setter
    def Subject(self, _subject: str):
        self['Subject'] = _subject

    @property
    def To(self) -> str:
        return self['To']

    @To.setter
    def To(self, _to: str):
        self['To'] = _to

    def send(self, *args):
        self.attach(MIMEText(self.content, *args))
        with SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(self['From'], "puiz yxql tnoe ivaa")
            server.send_message(self)
        return