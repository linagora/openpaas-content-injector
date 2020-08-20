#!/usr/bin/env python3

import linsharecli
import linshareapi.user as lin
import os
import sys
import configparser
import random
import argparse


dataPath = os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')

urls = configparser.ConfigParser()
urls.read(os.path.join(dataPath, 'Config','sitesUrl'))
host =  urls['Linshare']['url']

cred = configparser.ConfigParser()
cred.read(os.path.join(dataPath, 'Config', 'logins'))
logins = cred.sections()

verbose = False
debug = 0
loginInfo = {}


def initializeUuids(user, uuid):
    """Return a dict containing all the uuids for the mails in the config file
    They have been created if they were not present in the Linshare database"""

    loginInfo = {}
    mail , password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    for log in logins:
        response = cli.shares.core.list("autocomplete/"+cred[log]['mail'] +"?threadUuid=" + uuid + "&type=THREAD_MEMBERS")
        accountInfo = response[0]
        loginInfo.update({log : accountInfo})
    return loginInfo


def upload_file(user, filePath):
    "Upload a file on the user personnal space"
    mail , password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    url = "documents?async=False"
    upl = cli.documents.core.upload(filePath, url, progress_bar = False)
    uuid = upl['uuid']
    return uuid


def get_names(user):
    "Returns the names and ids of the files in the personnal space of user"
    mail , password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    lst = cli.documents.list()
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    names = [(item['uuid'], item['name']) for item in lst]
    return names


def share_file(user, fileUuid, recipients:list):
    "Share a file in the personnal space of user with the recipients"
    mail , password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    rec =  [{'mail' : mail} for mail in recipients]
    doc = cli.shares.create({"recipients":rec,
            "documents":[fileUuid]})
    return doc


def upshare(user, filePath, recipients:list):
    "Upload and share a file with the recipients"
    mail , password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    url = "documents?async=False"
    json = cli.documents.core.upload(filePath, url, progress_bar = False)
    fileUuid = json['uuid']
    rec =  [{'mail' : cred[rec]['mail']} for rec in recipients]
    rbu = cli.shares.get_rbu()

    rbu.set_value('documents', [fileUuid])
    rbu.set_value('recipients', rec)
    data = rbu.to_resource()
    shr = cli.shares.create(data)
    return shr


def create_sharedspace(user, files, wkName, coworkers, roles = []):
    "Create a new shared space, roles and coworkers must have the same length"
    global loginInfo

    mail , password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)


    def build_role(value):
        """Transform the input (string) into an role object."""
        return {
                'name': value,
                'uuid': cli.shared_spaces.members.roles.get(value)
                }

    rbu = cli.shared_spaces.get_rbu()
    rbu.set_value('name', wkName)
    data = rbu.to_resource()
    ssp = cli.shared_spaces.create(data)
    ssUuid = ssp['uuid']


    loginInfo = initializeUuids(user, ssUuid)

    rbu = cli.shared_spaces.members.get_rbu()
    rbu.set_value('node', {'uuid' : ssUuid})

    for k in range(len(coworkers)):
        user = coworkers[k]
        accountUuid = loginInfo[user]['userUuid']
        rbu.set_value('userMail', user)
        rbu.set_value('account', {'uuid' : accountUuid})
        if roles:
            rbu.set_value('role', build_role(roles[k].upper()))
        data = rbu.to_resource()
        mem = cli.shared_spaces.members.create(data)

    rbu = cli.workgroup_folders.get_rbu()
    rbu.set_value('workGroup', ssUuid)

    for filePath in files:
        url = "%(base)s/%(wg_uuid)s/nodes" % {
            'base': cli.workgroup_folders.local_base_url,
            'wg_uuid': ssUuid
        }
        upl = cli.workgroup_folders.core.upload(filePath, url, progress_bar=False)

    return ssUuid


def main(language:str):
    "Fill Linshare with some files in all the different spaces"
    admin = logins[0]

    listFiles = os.listdir(os.path.join(dataPath, 'Linshare', 'Files', language))

    with open(os.path.join(dataPath, 'Linshare', 'SsNames', language)) as ssfile:
        ssNames = ssfile.read().splitlines()

    fileNames = random.sample(listFiles, 3)
    filePaths = [os.path.join(dataPath, 'Linshare', 'Files', language, fileName) for fileName in fileNames]
    others = list(logins)
    others.remove(admin)
    create_sharedspace(admin, filePaths, random.choice(ssNames), others)

    for log in logins:
        fileName = random.choice(listFiles)
        filePath = os.path.join(dataPath, 'Linshare', 'Files', language, fileName)
        upload_file(log, filePath)

        fileName = random.choice(listFiles)
        filePath = os.path.join(dataPath, 'Linshare', 'Files', language, fileName)
        others = list(logins)
        others.remove(log)
        upshare(log, filePath, random.sample(others, random.randint(1,3)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language")
    parsing = parser.parse_args()
    main(parsing.language)