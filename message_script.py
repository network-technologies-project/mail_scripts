import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email
import imaplib
import json

def write(username, password, addresee, body):
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = addresee
    msg['Subject'] = "Test Subject"
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    text = msg.as_string()
    server.sendmail(username, addresee, text)
    server.quit()

class Server(object):

    def __init__(self, mail, users):
        self.login = mail["login"]
        self.password = mail["password"]
        self.admins = []
        self.users = []
        for user in users:
            if ("admin" == user["role"]):
                self.admins.append(user["mail"])
            self.users.append(user["mail"])
        self.command_stack = {"users": [],
                              "admins": []}
        self.command_list = ["add", "delete", "send"]        

    def read_mails(self):
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imap.login(self.login, self.password)
        imap.select('INBOX')
        unread_msg_nums = []
        for user in self.users:
            status, response = imap.uid('search', None, 'UNSEEN', 'FROM {0}'.format(user))
            if status == 'OK':
                unread_msg_nums.append((user, response[0].split()))
        for user, user_unread_msg_nums in unread_msg_nums:
            for e_id in user_unread_msg_nums:
                command = {}
                e_id = e_id.decode('utf-8')
                _, response = imap.uid('fetch', e_id, '(RFC822)')
                html = response[0][1].decode('utf-8')
                email_message = email.message_from_string(html)
                for _ in [k.get_payload() for k in email_message.walk() if k.get_content_type() == 'text/plain']:
                    text = _.split()
                    length = len(text)
                    for i in range(length):
                        if (text[i] in self.command_list):
                            if i != length-1:
                                c = [text[i], text[i+1]]
                            else:
                                с = [text[i], ""]
                            if user in self.admins:
                                self.command_stack["admins"].append(c)
                            else:
                                self.command_stack["users"].append(c)
        print(self.command_stack)

    def analize_command(self):
        for com in self.command_stack["users"]:
            if com[0] == "send":
                self.send_info()
        for com in self.command_stack["admins"]:
            if com[0] == "send":
                self.send_info()

    def send_info(self):
        with open("info.txt", "r") as file:
            print(file)
            for user in self.users:
                write(self.login, self.password, user, file.read())

    def process(self):
        self.read_mails()
        self.analize_command()




def read(username, password, sender_of_interest=None):
    # Login to INBOX
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(username, password)
    imap.select('INBOX')
    if sender_of_interest:
        status, response = imap.uid('search', None, 'UNSEEN', 'FROM {0}'.format(sender_of_interest))
    else:
        status, response = imap.uid('search', None, 'UNSEEN')
    if status == 'OK':
        unread_msg_nums = response[0].split()
    else:
        unread_msg_nums = []
    data_list = []
    for e_id in unread_msg_nums:
        data_dict = {}
        e_id = e_id.decode('utf-8')
        _, response = imap.uid('fetch', e_id, '(RFC822)')
        html = response[0][1].decode('utf-8')
        email_message = email.message_from_string(html)
        data_dict['mail_to'] = email_message['To']
        data_dict['mail_subject'] = email_message['Subject']
        data_dict['mail_from'] = email.utils.parseaddr(email_message['From'])
        data_dict['body'] = email_message.get_payload()
        for _ in [k.get_payload() for k in email_message.walk() if k.get_content_type() == 'text/plain']:
            print(_)
        data_list.append(data_dict)
    print(data_list)
    if (data_list != []):
    	write(username, password, sender_of_interest)

with open("users.json", "r") as users_file:
    users_root = json.load(users_file)
users = users_root["mail_of_interest"]

with open("servers_mail.json", "r") as mails_file:
    mails_root = json.load(mails_file)
mails = mails_root["mails"]

for mail in mails:
    serv = Server(mail, users)
    serv.process() 

