#!/usr/bin/env python3

import os
import sys
import configparser
import random
import argparse
import linshareapi.user as lin


dataPath = os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')

urls = configparser.ConfigParser()
urls.read(os.path.join(dataPath, 'Config', 'sitesUrl'))
host = urls['Linshare']['url']

cred = configparser.ConfigParser()
cred.read(os.path.join(dataPath, 'Config', 'loginOpenPaas'))
logins = cred.sections()

verbose = False
debug = 0
login_info = {}


def initialize_uuids(user, uuid):
    """Return a dict containing all the uuids for the mails in the config file
    They have been created if they were not present in the Linshare database"""

    global login_info
    mail, password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    for log in logins:
        response = cli.shares.core.list("autocomplete/"+cred[log]['mail'] +
                                        "?threadUuid=" + uuid + "&type=THREAD_MEMBERS")
        account_info = response[0]
        login_info.update({log : account_info})
    return login_info


def upload_file(user, file_path):
    "Upload a file on the user personnal space"
    mail, password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    url = "documents?async=False"
    upl = cli.documents.core.upload(file_path, url, progress_bar=False)
    uuid = upl['uuid']
    return uuid


def get_names(user):
    "Returns the names and ids of the files in the personnal space of user"
    mail, password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    lst = cli.documents.list()
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    names = [(item['uuid'], item['name']) for item in lst]
    return names


def share_file(user, file_uuid, recipients: list):
    "Share a file in the personnal space of user with the recipients"
    mail, password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    rec = [{'mail' : mail} for mail in recipients]
    doc = cli.shares.create({"recipients":rec,
                             "documents": [file_uuid]})
    return doc


def upshare(user, file_path, recipients: list):
    "Upload and share a file with the recipients"
    mail, password = cred[user]['mail'], cred[user]['password']
    cli = lin.UserCli(host, mail, password, verbose, debug)
    cli.nocache = True
    if not cli.auth():
        sys.exit(1)
    url = "documents?async=False"
    json = cli.documents.core.upload(file_path, url, progress_bar=False)
    file_uuid = json['uuid']
    rec = [{'mail' : cred[rec]['mail']} for rec in recipients]
    rbu = cli.shares.get_rbu()

    rbu.set_value('documents', [file_uuid])
    rbu.set_value('recipients', rec)
    data = rbu.to_resource()
    shr = cli.shares.create(data)
    return shr


def create_sharedspace(user, files, wk_name, coworkers, roles=[]):
    "Create a new shared space, roles and coworkers must have the same length"

    mail, password = cred[user]['mail'], cred[user]['password']
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
    rbu.set_value('name', wk_name)
    data = rbu.to_resource()
    ssp = cli.shared_spaces.create(data)
    ss_uuid = ssp['uuid']

    initialize_uuids(user, ss_uuid)

    rbu = cli.shared_spaces.members.get_rbu()
    rbu.set_value('node', {'uuid' : ss_uuid})

    for k in range(len(coworkers)):
        user = coworkers[k]
        account_uuid = login_info[user]['userUuid']
        rbu.set_value('userMail', user)
        rbu.set_value('account', {'uuid' : account_uuid})
        if roles:
            rbu.set_value('role', build_role(roles[k].upper()))
        data = rbu.to_resource()
        cli.shared_spaces.members.create(data)

    rbu = cli.workgroup_folders.get_rbu()
    rbu.set_value('workGroup', ss_uuid)

    for file_path in files:
        url = "%(base)s/%(wg_uuid)s/nodes" % {
            'base': cli.workgroup_folders.local_base_url,
            'wg_uuid': ss_uuid
        }
        cli.workgroup_folders.core.upload(file_path, url, progress_bar=False)

    return ss_uuid


def main(language: str):
    "Fill Linshare with some files in all the different spaces"
    admin = logins[0]

    list_files = os.listdir(os.path.join(dataPath, 'Linshare', 'Files', language))

    with open(os.path.join(dataPath, 'Linshare', 'SsNames', language)) as ssfile:
        ss_names = ssfile.read().splitlines()

    file_names = random.sample(list_files, 3)
    file_paths = [os.path.join(dataPath, 'Linshare', 'Files', language, file_name)
                  for file_name in file_names]
    others = list(logins)
    others.remove(admin)
    create_sharedspace(admin, file_paths, random.choice(ss_names), others)

    for log in logins:
        file_name = random.choice(list_files)
        file_path = os.path.join(dataPath, 'Linshare', 'Files', language, file_name)
        upload_file(log, file_path)

        file_name = random.choice(list_files)
        file_path = os.path.join(dataPath, 'Linshare', 'Files', language, file_name)
        others = list(logins)
        others.remove(log)
        upshare(log, file_path, random.sample(others, random.randint(1, 3)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language")
    parsing = parser.parse_args()
    main(parsing.language)
