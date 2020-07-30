#!/usr/bin/env python3

import linsharecli
import linshareapi.user as lin
import os
import sys
import configparser


dataPath = os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')
urls = configparser.ConfigParser()
urls.read(os.path.join(dataPath, 'Config','sitesUrl'))
host =  urls['Linshare']['url']

cred = configparser.ConfigParser()
cred.read(os.path.join(dataPath, 'Config', 'logins'))
logins = cred.sections()

user_, password_ = cred[logins[0]]['login'], cred[logins[0]]['password']
verbose = True
debug = 1
path = '../SW contract'
mail = cred[logins[1]]['login']


def upload_file(user, password, path_to_the_file):
    cli = lin.UserCli(host, user, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    upl = cli.documents.upload(path)
    uuid = upl['uuid']
    return uuid


def get_names(user, password):
    cli = lin.UserCli(host, user, password, verbose, debug)
    lst = cli.documents.list()
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    names = [(item['uuid'], item['name']) for item in lst]
    return names


def share_file(user, password, file_uuid, shares:list):
    cli = lin.UserCli(host, user, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    for mail in shares:
        lst = cli.shares.create({"recipients":[{"mail":mail}],
            "documents":[file_uuid],"mailingListUuid":[],
            "secured":True,"creationAcknowledgement":True,
            "enableUSDA":True,"notificationDateForUSDA":1596292604847,"sharingNote":"",
            "subject":"","message":""})
        print(lst)



#print(upload_file(user_, password_, path))
#print(get_names(user_, password_))
print(share_file(user_, password_, get_names(user_, password_)[0][0], [mail]))