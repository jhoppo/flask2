import smtplib
from jinja2 import Environment
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
class JiehongEmail:
    def __init__(self, sender, sender_password, smtp_host, smtp_host_port):
        self.sender_password = sender_password
        self.sender = sender
        self.msg = MIMEMultipart()
        self.msg['From'] = self.sender
        self.smtp_server = smtplib.SMTP(smtp_host,smtp_host_port)
        self.smtp_server.starttls()
        self.smtp_server.login(self.sender, self.sender_password)
    def MailSubject(self, subject):
        self.msg['Subject'] = subject
    def MailContent(self, body):
        self.msg.attach(MIMEText(body, "HTML", 'UTF-8'))
    def SendTo(self, receivers):
        self.msg['To'] = ",".join(receivers)
    def CcTo(self, ccs):
        self.msg['Cc'] = ",".join(ccs)
    def SendMail(self):
        receivers = f"{self.msg['To']}, {self.msg['Cc']}".split(",")
        try:
            self.smtp_server.sendmail(self.sender, receivers, self.msg.as_string())
            return "Success"
        except:
            return "Some of information is wrong, you fucking idiot!"
    def LogoutsmTP(self):
        self.smtp_server.quit()
# if __name__ == '__main__':
#     jhSend = JiehongEmail(sender='jack.hong@oppo-aed.tw',
#                           sender_password='Rliwn^0000',
#                           smtp_host='smtp.office365.com',
#                           smtp_host_port=587)
#     jhSend.MailSubject("test new class")
#     jhSend.MailContent(f"<h1>Hi</h1>,<hr> this is test mail, test at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     jhSend.SendTo(['sock40038@gmail.com', 'shong9887@gmail.com'])
#     jhSend.CcTo(['jiehongmakemoney@gmail.com',])
#     jhSend.SendMail()
#     jhSend.LogoutsmTP()
