#!/usr/bin/env python3

import argparse
import subprocess
import os
from datetime import datetime
import sys
import configparser
import EmailSending
import Linshare

log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'Logs'))
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'RawData'))
script_path = os.path.abspath(os.path.dirname(__file__))
FNULL = open(os.devnull, 'w')

# create parser
parser = argparse.ArgumentParser()

# add arguments to the parser
parser.add_argument("language")
parser.add_argument("month")
parser.add_argument("day")
parser.add_argument("year")

# parse the arguments
parsing = parser.parse_args()
date_exec = datetime.now()

#Execute first RobotFramework script: Twake
print("Sending messages in Twake...", end=' ', flush=True)
first_script = ['robot', '--outputdir', log_path,
                '--noncritical', 'all',
                '--variable', f'LANGUAGE:{parsing.language}',
                '--variable', f'PATH:{data_path}',
                os.path.join(script_path, 'Twake.robot')]
subprocess.run(first_script, cwd=log_path, stdout=FNULL)
print(" "*32, datetime.now() - date_exec)
date_exec = datetime.now()

#Execute second RF script: Create Event
print("Creating events in the calendar...", end=' ', flush=True)
second_script = ['robot', '--outputdir', log_path,
                 '--noncritical', 'all',
                 '--variable', f'LANGUAGE:{parsing.language}',
                 '--variable', f'PATH:{data_path}',
                 '--variable', f'MONTH:{parsing.month}',
                 '--variable', f'DAY:{parsing.day}',
                 '--variable', f'YEAR:{parsing.year}',
                 os.path.join(script_path, 'Calendar.robot')]
subprocess.run(second_script, cwd=log_path, stdout=FNULL)
print(" "*26, datetime.now() - date_exec)
date_exec = datetime.now()

#Execute third script (python): Send emails
print("Sending emails...", end=' ', flush=True)
event_list = EmailSending.main(parsing.language, parsing.month, parsing.day, parsing.year)

event_to_create = {}
cred = configparser.ConfigParser()
cred.read(os.path.join(data_path, 'Config', 'loginOpenPaas'))

logins = cred.sections()
for l in logins:
    event_to_create.update({cred[l]['mail']: []})

for event in event_list:
    org = event['organizer']
    event.pop('organizer')
    event_to_create[org].append(event)
file_path = os.path.join(data_path, 'Events', 'EventsFromMails.py')
new_file = open(file_path, 'w')
text = 'VariableDict=' + str(event_to_create)
new_file.write(text)
new_file.close()
third_script = ['robot', '--outputdir', log_path,
                '--noncritical', 'all',
                '--variable', f'PATH:{data_path}',
                '--variablefile', file_path,
                os.path.join(script_path, 'CalendarLinksWithMails.robot')]
subprocess.run(third_script, cwd=log_path, stdout=FNULL)
print(" "*43, datetime.now() - date_exec)
date_exec = datetime.now()

#Execute the fourth script (python): Fill Linshare
print("Filling Linshare...", end=' ', flush=True)
Linshare.main(parsing.language)
print(" "*41, datetime.now() - date_exec)
date_exec = datetime.now()
