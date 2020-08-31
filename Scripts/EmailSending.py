#!/usr/bin/env python3

import datetime
import os
import random
import argparse
import calendar
import configparser
import requests

s = requests.session()
access_token = None
header_auth = None
data_path = os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')

urls = configparser.ConfigParser()
urls.read(os.path.join(data_path, 'Config', 'sitesUrl'))
meta_url = urls['Email']['url']

server_url = os.path.join(meta_url, 'jmap')
auth_url = os.path.join(meta_url, 'authentication')
upload_url = os.path.join(meta_url, 'upload')
download_url = os.path.join(meta_url, 'download')


def get_access_token(username: str, password: str, verbose=False) -> str:
    "First request: get the authentication token"

    headers = {"Accept": "application/json", "Content-Type": "application/json; charset=UTF-8"}
    body = {"username": username,
            "clientName": "Mozilla Firefox",
            "clientVersion": "67.0",
            "deviceName": "Sending emails to fill OP"}


    response = s.post(auth_url, headers=headers, json=body)
    first_json = response.json()

    if verbose:
        print("Response of the first request : ", response)
        print("First json : ", first_json)

    token = first_json['continuationToken']
    body_second = {"token": token, "method": "password", "password": password}

    response = s.post(auth_url, headers=headers, json=body_second)

    json_second = response.json()

    if verbose:
        print("Response of the second request ", response)
        print("Second json : ", json_second)

    return json_second['accessToken']


def set_tokens(username: str, password: str) -> None:
    "Set the global variables in order to use them for the next requests"

    global access_token, header_auth
    access_token = get_access_token(username, password)
    header_auth = {"Accept": "application/json", "Content-Type": "application/json; charset=UTF-8",
                   "Authorization": access_token}


def send_mail(sender: str,
              sender_name: str,
              receivers: list,
              copies: list = [],
              subject='Mail subject',
              message="Message to be sent",
              outbox_id='Error',
              attachments=[],
              day=None, month=None, year=None, hour=10, minutes=0,
              verbose=False) -> (str, str):

    r"""Send an email from the sender adress the receivers, with copy for copies.
    Subject, body, date of the message... can be set

    :param sender: email of the sender - must be the same as the one used for authentification
    :param sender_name: name of the sender, as displayed in the email
    :param receivers: list of dict with email and name as keys
    :param message: message body
    :param subject: (optionnal) title of the email
    :params date and time of sending: (optionnal)"""

    if day is None or month is None or year is None:
        today = datetime.datetime.now()
        date = today.replace(hour=today.hour-2).isoformat()+'Z'
    else:
        date = datetime.datetime(year, month, day, (hour-2)%24, minutes).isoformat()+'Z'

    creation_id = 'FillingOP' + str(random.random())[2:]
    body_sending = [["setMessages", {
        "create" : {
            creation_id : {
                "bcc" : [],
                "cc" : copies,
                "from" : {
                    "email" : sender,
                    "name" : sender_name
                },
                "mailboxIds" : [outbox_id],
                "htmlBody" : message,
                "replyTo" : [{
                    "email" : sender,
                    "name" : sender_name
                }],
                "subject" : subject,
                "to" : receivers,
                "date" : date,
                "attachments" : attachments
            }
        }
    },
                     "#0"]]

    response = s.post(server_url, headers=header_auth, json=body_sending, verify=False)
    mail_json = response.json()

    mail_id = mail_json[0][1]['created'][creation_id]['id']

    if verbose:
        print(mail_json[0][1]['created'][creation_id])

    return mail_id, creation_id


def getoutbox_id() -> str:
    "Get the ID ouf the outbox folder, needed to send emails for ex."

    body_inbox_list = [["getMailboxes", {}, "#0"]]

    response = s.post(server_url, headers=header_auth, json=body_inbox_list, verify=False)
    box_json = response.json()

    outbox_id = None
    for mail_folder in box_json[0][1]['list']:
        if mail_folder['name'] == 'Outbox':
            outbox_id = mail_folder['id']
            return outbox_id
    return 'Error : No outbox found'


def upload_file(file_path: str) -> dict:
    "Upload the file from the path and return the dictionnary to add to the attachments"

    header_upload = header_auth
    content_type = os.path.splitext(file_path)[1]

    if content_type in ['.png', '.jpeg', '.gif', '.jpg']:
        header_upload["Content-Type"] = 'image/'+ content_type[1:]

    elif content_type in ['.pdf', '.json', '.xml']:
        header_upload["Content-Type"] = 'application/'+ content_type[1:]

    elif content_type == '.odt':
        header_upload["Content-Type"] = 'application/vnd.oasis.opendocument.text'

    elif content_type == '.ods':
        header_upload["Content-Type"] = 'application/vnd.oasis.opendocument.spreadsheet'

    elif content_type == '.odp':
        header_upload["Content-Type"] = 'application/vnd.oasis.opendocument.presentation'


    response = s.post(upload_url, headers=header_upload, verify=False, data=file_path)
    upload_json = response.json()
    file_name = os.path.basename(file_path)

    attachments = {"blobId" : upload_json['blobId'],
                   "type" : upload_json['type'],
                   "name" : file_name,
                   "size": upload_json['size'],
                   "url": os.path.join(download_url, upload_json['blobId'], file_name),
                   "isInline" : False}

    return attachments


def calcul_date(sending_date: datetime.date, weekday: str, hours: str):
    """Returns the date of the next 'weekday' after the given date"""

    conversion = {'mo' : 0, 'tu' : 1, 'we' : 2, 'th' : 3, 'fr' : 4, 'to' : 15}
    hourb, houre = hours.split('-')
    hourb = hourb[:2] + ':00 ' + hourb[2:].upper()
    houre = houre[:2] + ':00 ' + houre[2:].upper()
    if weekday == 'to':
        return sending_date, hourb, houre
    var_date = sending_date + datetime.timedelta(days=1)
    while var_date.weekday() != conversion[weekday]:
        var_date = var_date + datetime.timedelta(days=1)
    return var_date, hourb, houre


def main(language: str, month: str, day: str, year: str, mail_a_day: int = 2) -> list(dict()):
    """Send an (optionnaly) given number of mails for each days beetween
    the given date and the end of the month"""

    cred = configparser.ConfigParser()
    cred.read(os.path.join(data_path, 'Config', 'loginOpenPaas'))
    logins = cred.sections()

    list_messages = os.listdir(os.path.join(data_path, 'Mails', language))
    list_attachments = os.listdir(os.path.join(data_path, 'Linshare', 'Files', language))
    int_day = int(day)
    int_month = int(month)
    int_year = int(year)

    event_list = []

    for k in range(int_day, calendar.monthrange(int_year, int_month)[1]):
        sending_date = datetime.date(int_year, int_month, k)
        if sending_date.weekday() < 5:
            for _ in range(mail_a_day):

                #Select an email:
                message_name = list_messages[random.randrange(len(list_messages))]
                with open(os.path.join(data_path, 'Mails', language, message_name)) as message_file:
                    message = message_file.read()
                subject, *attribute = message_name.split('_')


                #Select one or more email adresses
                #Personnalize the mail

                copies = []
                attachments = []
                if 'copy' in attribute:
                    sender, rec, cop = random.sample(range(len(logins)), 3)
                    receiver = cred[logins[rec]]
                    copy = cred[logins[cop]]
                    real_message = message.format(receiver=receiver['first_name'],
                                                  sender=logins[sender],
                                                  sender_mail=cred[logins[sender]]['mail'],
                                                  in_copy=copy['first_name'])
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]
                    copies = [{'email' : copy['mail'], 'name' : logins[cop]}]

                elif 'many' in attribute:
                    sender, *rec = random.sample(range(len(logins)), len(logins))
                    receivers = []
                    real_message = message.format(receiver=cred[logins[rec[0]]]['first_name'],
                                                  sender=logins[sender],
                                                  sender_mail=cred[logins[sender]]['mail'])
                    for j in rec:
                        temp = cred[logins[j]]
                        receivers.append({'email' : temp['mail'], 'name' : logins[j]})

                elif 'attach' in attribute:
                    sender, rec = random.sample(range(len(logins)), 2)
                    receiver = cred[logins[rec]]
                    real_message = message.format(receiver=receiver['first_name'],
                                                  sender=logins[sender],
                                                  sender_mail=cred[logins[sender]]['mail'])
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]
                    if len(attribute) > 1:
                        file_name = attribute[1]
                    else:
                        file_name = list_attachments[random.randrange(len(list_attachments))]
                    file_path = os.path.join(data_path, 'Linshare', 'Files', language, file_name)
                    attachments.append(upload_file(file_path))

                elif 'event' in attribute:
                    sender, rec = random.sample(range(len(logins)), 2)
                    receiver = cred[logins[rec]]

                    _, event_name, weekday, hours = attribute
                    event_date, hour1, hour2 = calcul_date(sending_date, weekday, hours)
                    real_message = message.format(receiver=receiver['first_name'],
                                                  sender=logins[sender],
                                                  sender_mail=cred[logins[sender]]['mail'],
                                                  event_date=event_date.strftime("%A %d."))
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]
                    event_list.append({'date' : event_date.strftime("%a %Y/%m/%d"),
                                       'event_name' : event_name,
                                       'begHour' : hour1, 'endHour' : hour2,
                                       'organizer' : cred[logins[sender]]['mail']})

                else:
                    sender, rec = random.sample(range(len(logins)), 2)
                    receiver = cred[logins[rec]]
                    real_message = message.format(receiver=receiver['first_name'],
                                                  sender=logins[sender],
                                                  sender_mail=cred[logins[sender]]['mail'])
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]

                #Set tokens for the corresponding login
                send = cred[logins[sender]]
                mail, passw = send['mail'], send['password']
                set_tokens(mail, passw)

                outbox_id = getoutbox_id()

                send_mail(sender=mail, sender_name=logins[sender],
                          subject=subject, message=real_message,
                          receivers=receivers, copies=copies,
                          outbox_id=outbox_id,
                          year=sending_date.year, day=sending_date.day, month=sending_date.month,
                          hour=random.randint(9, 20), minutes=random.randint(0, 59))


    return event_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language")
    parser.add_argument("month")
    parser.add_argument("day")
    parser.add_argument("year")
    parsing = parser.parse_args()
    main(parsing.language, parsing.month, parsing.day, parsing.year)
