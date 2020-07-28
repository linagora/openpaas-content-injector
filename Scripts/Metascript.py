import argparse
import subprocess
import os
import EmailSending

logPath= os.path.join(os.path.dirname(__file__), os.pardir, 'Logs')
dataPath= os.path.join(os.path.dirname(__file__), os.pardir, 'RawData')
scriptPath = os.path.abspath(os.path.dirname(__file__))
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

#Execute first RobotFramework script: Twake
print("Sending messages in Twake...")
firstScript = ['robot', '--outputdir', logPath,
                        '--noncritical', 'all',
                        '--variable', f'LANGUAGE:{parsing.language}', 
                        '--variable', f'PATH:{dataPath}', 
            os.path.join(scriptPath, 'Twake.robot')]
subprocess.run(firstScript, cwd=logPath, stdout=FNULL)

#Execute second RF script: Create Event
print("Creating events in the calendar...")
secondScript = ['robot','--outputdir', logPath,
                        '--noncritical', 'all',
                        '--variable', f'LANGUAGE:{parsing.language}',
                        '--variable', f'PATH:{dataPath}', 
                        '--variable', f'MONTH:{parsing.month}', 
                        '--variable', f'DAY:{parsing.day}', 
                        '--variable', f'YEAR:{parsing.year}', 
            os.path.join(scriptPath,'Calendar.robot')]
subprocess.run(secondScript, cwd=logPath, stdout=FNULL)

#Execute third script (python): Send emails
print("Sending emails...")
eventList = EmailSending.main(parsing.language, parsing.month, parsing.day, parsing.year)

eventToCreate = {}
cred = open(os.path.join(dataPath, 'Config', 'logins'))
credentials = cred.read()
logins = credentials.splitlines()
for l in logins:
    eventToCreate.update({l.split('|')[0]:[]})
cred.close()
for event in eventList:
    org = event['organizer']
    event.pop('organizer')
    eventToCreate[org].append(event)
print(eventToCreate)
thirdScript = ['robot','--outputdir', logPath,
                        '--noncritical', 'all',
                        '--variable', f'PATH:{dataPath}', 
                        '--variable', f'VariableDict:{eventToCreate}',
            os.path.join(scriptPath,'CalendarLinksWithMails.robot')]
subprocess.run(thirdScript, cwd=logPath, stdout=FNULL)