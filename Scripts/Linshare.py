import linsharecli
import linshareapi.user as lin
import os

dataPath = os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')
urls = open(os.path.join(dataPath, 'Config','sitesUrl'))
host =  urls.read().splitlines()[4]
urls.close()

cred = open(os.path.join(dataPath, 'Config', 'logins'))
credentials = cred.read()
logins = credentials.splitlines()
cred.close()

user_, password_, *_ = logins[0].split('|')
verbose = True
debug= 1
path = '../SW contract'
mail, *_ = logins[1].split('|')


def upload_file(user, password, path_to_the_file):
    cli = lin.UserCli(host, user, password, verbose, debug)
    upl = cli.documents.upload(path)
    uuid = upl['uuid']
    return uuid

def get_names(user, password):
    cli = lin.UserCli(host, user, password, verbose, debug)
    lst = cli.documents.list()
    names = [(item['uuid'], item['name']) for item in lst]
    return names

def share_file(user, password, file_uuid, shares:list):
    cli = lin.UserCli(host, user, password, verbose, debug)
    for mail in shares:
        lst = cli.shares.share(file_uuid, mail)
        print(lst)



#print(upload_file(user_, password_, path))
#print(get_names(user_, password_))
print(share_file(user_, password_, get_names(user_, password_)[0][0], [mail]))