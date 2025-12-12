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

    @classmethod
    def to_html(cls, text: str) -> str:
        return f"""
<!doctype html>
<html>    
    <style>
        .styled-table {{
            border-collapse: collapse;
            width: 100%;
            text-align: right;
        }}
        .styled-table th, .styled-table td {{
            border: 1px solid #ccc;
            padding: 8px;
            font-weight: 500;
        }}
    </style>
    <body>
        <p>{text}</p>
    </body>
</html>
"""

    def send(self, *args):
        self.attach(MIMEText(self.content, *args))
        with SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(self['From'], "puiz yxql tnoe ivaa")
            server.send_message(self)
        return