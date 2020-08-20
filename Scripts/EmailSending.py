#!/usr/bin/env python3

import requests
import json
import datetime
import os
import random
import argparse
import calendar
import configparser

s = requests.session()
accessToken = None
headerAuth = None
dataPath = os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')

urls = configparser.ConfigParser()
urls.read(os.path.join(dataPath, 'Config','sitesUrl'))
metaUrl =  urls['Email']['url']

serverUrl = os.path.join(metaUrl, 'jmap')
authUrl = os.path.join(metaUrl, 'authentication')
uploadUrl = os.path.join(metaUrl, 'upload')
downloadUrl = os.path.join(metaUrl, 'download')


def getAccessToken(username: str, password: str, verbose=False) -> str:
    "First request: get the authentication token"

    headers= {"Accept": "application/json", "Content-Type": "application/json; charset=UTF-8"}
    body = {"username": username,
        "clientName": "Mozilla Firefox",
        "clientVersion": "67.0",
        "deviceName": "Sending emails to fill OP"}


    response = s.post(authUrl, headers=headers, json=body)
    firstJson = response.json()

    if verbose:
        print("Response of the first request : ", response)
        print("First json : ", firstJson)

    token = firstJson['continuationToken']
    bodySecond = {"token": token, "method": "password",    "password": password}

    response = s.post(authUrl, headers=headers, json = bodySecond)

    jsonSecond = response.json()

    if verbose:
        print("Response of the second request ", response)
        print("Second json : ", jsonSecond)

    return jsonSecond['accessToken']


def setTokens(username: str, password: str) -> None:
    "Set the global variables in order to use them for the next requests"

    global accessToken, headerAuth
    accessToken = getAccessToken(username, password)
    headerAuth = {"Accept": "application/json", "Content-Type": "application/json; charset=UTF-8", "Authorization": accessToken}


def sendMail(sender : str,
            senderName : str,
            receivers : list,
            cc:list = [],
            subject = 'Mail subject',
            message = "Message to be sent",
            outboxId = 'Error',
            attachments = [],
            day = None, month = None, year = None, hour = 10, minutes = 0,
            verbose = False
            ) -> (str, str):

    r"""Send an email from the sender adress the receivers, with copy for cc. Subject, body, date of the message... can be set

    :param sender: email of the sender - must be the same as the one used for authentification
    :param senderName: name of the sender, as displayed in the email
    :param receivers: list of dict with email and name as keys
    :param message: message body
    :param subject: (optionnal) title of the email
    :params date and time of sending: (optionnal)"""
    
    if day == None or month == None or year == None:
        d = datetime.datetime.now()
        date = d.replace(hour=d.hour-2).isoformat()+'Z'
    else:
        date = datetime.datetime(year, month, day, (hour-2)%24,minutes).isoformat()+'Z'
    
    creationID = 'FillingOP' + str(random.random())[2:]
    bodySending = [["setMessages",{
        "create" : {
            creationID : {
                "bcc" : [],
                "cc" : cc,
                "from" : {
                    "email" : sender,
                    "name" : senderName
                },
                "mailboxIds" : [outboxId],
                "htmlBody" : message,
                "replyTo" : [{
                    "email" : sender,
                    "name" : senderName
                }],
                "subject" : subject,
                "to" : receivers,
                "date" : date,
                "attachments" : attachments
            }
        }
    },
    "#0"]]

    response = s.post(serverUrl, headers= headerAuth, json= bodySending, verify= False)
    mailJson  = response.json()
    
    mailId = mailJson[0][1]['created'][creationID]['id']

    if verbose:
        print(mailJson[0][1]['created'][creationID])

    return mailId, creationID


def getOutboxID() -> str:
    "Get the ID ouf the outbox folder, needed to send emails for ex."

    bodyInboxList = [["getMailboxes",{},"#0"]]

    response = s.post(serverUrl, headers= headerAuth, json= bodyInboxList, verify=False)
    boxJson = response.json()

    outboxID = None
    for mailFolder in boxJson[0][1]['list']:
        if mailFolder['name']== 'Outbox':
            outboxID = mailFolder['id']
            return outboxID
    return 'Error : No outbox found'
    

def uploadFile(filePath:str) -> dict:
    "Upload the file from the path and return the dictionnary to add to the attachments"

    headerUpload = headerAuth
    contentType = os.path.splitext(filePath)[1]

    if contentType in ['.png','.jpeg', '.gif']:
        headerUpload["Content-Type"] = 'image/'+ contentType[1:]

    elif contentType in ['.pdf', '.json', '.xml']:
        headerUpload["Content-Type"] = 'application/'+ contentType[1:]

    elif contentType == '.odt':
        headerUpload["Content-Type"] = 'application/vnd.oasis.opendocument.text'

    elif contentType == '.ods':
        headerUpload["Content-Type"] = 'application/vnd.oasis.opendocument.spreadsheet'

    elif contentType == '.odp':
        headerUpload["Content-Type"] = 'application/vnd.oasis.opendocument.presentation'


    response = s.post(uploadUrl, headers= headerUpload, verify=False, data= filePath)
    uploadJson = response.json()
    fileName = os.path.basename(filePath)

    attachments = {"blobId" : uploadJson['blobId'],
                    "type" : uploadJson['type'],
                    "name" : fileName,
                    "size": uploadJson['size'],
                    "url": os.path.join(downloadUrl, uploadJson['blobId'],fileName),
                    "isInline" : False}

    return attachments


def calculDate(sendingDate:datetime.date, weekday:str, hours:str):

    conversion = {'mo' : 0, 'tu' : 1, 'we' : 2, 'th' : 3, 'fr' : 4, 'to' : 15}
    hourb, houre = hours.split('-')
    hourb = hourb[:2] + ':00 ' + hourb[2:].upper()
    houre = houre[:2] + ':00 ' + houre[2:].upper()
    if weekday == 'to':
        return sendingDate, hourb, houre
    else:
        for k in range(1,8):
            varDate = sendingDate + datetime.timedelta(days=k)
            if varDate.weekday() == conversion[weekday]:
                return varDate, hourb, houre


def main(language:str, month:str, day:str, year:str, mailADay:int = 2) -> list(dict()):
    "Send an (optionnaly) given number of mails for each days beetween the given date and the end of the month"

    cred = configparser.ConfigParser()
    cred.read(os.path.join(dataPath, 'Config', 'logins'))
    logins = cred.sections()

    listMessages = os.listdir(os.path.join(dataPath, 'Mails', language))
    listAttachments = os.listdir(os.path.join(dataPath, 'Linshare', 'Files', language))
    d = int(day)
    m = int(month)
    y = int(year)

    eventList = []


    for k in range(d, calendar.monthrange(y, m)[1]):
        sendingDate = datetime.date(y, m, k)
        if sendingDate.weekday()<5:
            for _ in range(mailADay):

                #Select an email:
                messageName = listMessages[random.randrange(len(listMessages))]
                with open(os.path.join(dataPath, 'Mails', language, messageName)) as messageFile:
                    message = messageFile.read()
                subject, *attribute = messageName.split('_')

                
                #Select one or more email adresses
                #Personnalize the mail

                cc = []
                attachments = []
                if 'copy' in attribute:
                    sender, rec, cop = random.sample(range(len(logins)), 3)
                    receiver = cred[logins[rec]]
                    copy = cred[logins[cop]]
                    realMessage = message.format(receiver = receiver['first_name'], sender = logins[sender],
                                                senderMail = cred[logins[sender]]['mail'], in_copy = copy['first_name'])
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]
                    cc = [{'email' : copy['mail'], 'name' : logins[cop]}]
                
                elif 'many' in attribute:
                    sender, *rec = random.sample(range(len(logins)), len(logins))
                    receivers = []
                    realMessage = message.format(receiver = receiver['first_name'], sender = logins[sender],
                                                senderMail = cred[logins[sender]]['mail'])
                    for j in rec:
                        temp = cred[logins[j]]
                        receivers.append({'email' : temp['mail'], 'name' : logins[j]})

                elif 'attach' in attribute:
                    sender, rec = random.sample(range(len(logins)), 2)
                    receiver = cred[logins[rec]]
                    realMessage = message.format(receiver = receiver['first_name'], sender = logins[sender], senderMail = cred[logins[sender]]['mail'])
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]
                    if len(attribute) > 1:
                        fileName = attribute[1]
                    else:
                        fileName = listAttachments[random.randrange(len(listAttachments))]
                    filePath = os.path.join(dataPath, 'Linshare','Files', language, fileName)
                    attachments.append(uploadFile(filePath))

                elif 'event' in attribute:
                    sender, rec = random.sample(range(len(logins)), 2)
                    receiver = cred[logins[rec]]
                    
                    _, eventName, weekday, hours = attribute
                    eventDate, hour1, hour2 = calculDate(sendingDate, weekday, hours)
                    realMessage = message.format(receiver = receiver['first_name'], sender = logins[sender],
                                                senderMail = cred[logins[sender]]['mail'], eventDate = eventDate.strftime("%A %d."))
                    receivers = [{'email' : receiver['mail'], 'name' : logins[rec]}]
                    eventList.append({'date' : eventDate.strftime("%a %Y/%m/%d"), 'eventName' : eventName,
                                    'begHour' : hour1, 'endHour' : hour2, 'organizer' : cred[logins[sender]]['mail']})
                    
                else:
                    sender, rec = random.sample(range(len(logins)), 2)
                    receiver = cred[logins[rec]]
                    realMessage = message.format(receiver = receiver['first_name'], sender = logins[sender], senderMail = cred[logins[sender]]['mail'])
                    receivers=[{'email' : receiver['mail'], 'name' : logins[rec]}]

                #Set tokens for the corresponding login
                send = cred[logins[sender]]
                mail, passw = send['mail'], send['password']
                setTokens(mail, passw)

                outboxId = getOutboxID()

                a,b = sendMail(sender = mail, senderName = logins[sender], subject = subject, message = realMessage,
                        receivers = receivers, cc = cc,
                        outboxId = outboxId,
                        year = sendingDate.year, day = sendingDate.day, month = sendingDate.month, hour = random.randint(9,20), minutes = random.randint(0,59) )

                        
    return eventList


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language")
    parser.add_argument("month")
    parser.add_argument("day")
    parser.add_argument("year")
    parsing = parser.parse_args()
    main(parsing.language, parsing.month, parsing.day, parsing.year)