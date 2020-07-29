## Description
Use the scripts to prepare and fill the OpenPaas platform with data : mails, messages, events,... for demo or test purposes.

## Dependencies
The scripts uses Python3 and [Robotframework](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html) and also some aditionnal packages. If you don't have Python3 or Robotframework, you'll have to install them.

### Install Python3

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8
```

### Install RobotFramework and the other python dependencies
In order to install Robotframework and Selenium you will need to have [pip](http://pip-installer.org) installed and then install them with
```
pip install robotframework
pip install --upgrade robotframework-seleniumlibrary
```

You will also have to download a driver for your preferred browser, you can use webdrivermanager for that. For example
```
pip install webdrivermanager
webdrivermanager firefox --linkpath /usr/local/bin
```

You will also need two linshare packages :
```
pip install linshareapi
pip install linsharecli
```

## Running the script
### Clone the repository
You can clone the repository with
```
git clone https://github.com/linagora/openpaas-content-injector.git
cd openpaas-content-injector
```

### Set up
You will first need to rename the three files `logins.dist`, `loginTwake.dist` and `sitesUrl.dist` in the `RawData/Config` folder by removing the `.dist` and then complete them, with the data you will use (logins and urls of the OpenPaas different sites).


### Launch all the scripts
Once the repository cloned, you can launch all the scripts, giving the required arguments : language, month, day and year with (Warning, give the numbered args without any `0` in front of it : you must write `7` and no `07`)
```
python3 Scripts/Metascript.py English 7 14 2020
```

### Launch one script
You can also launch only one script with Python or Robotframework depending on which one you want. With Python3:
```
python3 Scripts/EmailSending.py Russian 7 14 2020
```
And with Robotframework:
```
robot --noncritical all --outputdir ./Logs --variable LANGUAGE:Russian Scripts/Twake.robot
robot --noncritical all --outputdir ./Logs --variable LANGUAGE:English --variable PATH:./RawData --variable MONTH:6 --variable DAY:29 --variable YEAR:2020 Scripts/Calendar.robot
```

