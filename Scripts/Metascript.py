import argparse
import subprocess
import os

logPath= os.path.join(os.path.abspath('..'), 'Logs')
dataPath=os.path.join(os.path.abspath('..'), 'RawData')
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
            os.path.join(os.path.abspath('.'), 'Twake.robot')]
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
            os.path.join(os.path.abspath('.'),'Calendar.robot')]
#subprocess.run(secondScript, cwd=logPath, stdout=FNULL)

#Execute third script (python): Send emails
print("Sending emails...")
thirdScript = ['python3', os.path.join(os.path.abspath('.'), 'EmailSending.py'), parsing.language, parsing.month, parsing.day, parsing.year]
subprocess.run(thirdScript)


