*** Settings ***
Documentation	Create an event in OpenPaas
Library         OperatingSystem
Library		  	SeleniumLibrary
Library		  	String
Library		  	Collections
Library    	  	DateTime
Library			ParsingForRf.py
Resource		Ressources.robot

*** Variables ***
#can/has to be changed in command line
${LOGIN OP}	https://an_open_pass_site/#/calendar

${PATH}		../RawData/


*** Tasks ***
Set Variables
	Set Global Variable	${PATH LOGINS}	${PATH}/Config/logins
	Parse A File	${PATH}/Config/sitesUrl
	${LOGIN OP}=	Get Item	Calendar	url
	Set Global Variable		${LOGIN OP}

Create The Events In The List
	Reinitialize Parser
	Parse A File	${PATH LOGINS}
    ${logins}=	Get Sections List
	${Size}=	Evaluate	len(${logins})
	FOR	${k}	IN RANGE	${Size}
		Set Global Variable	${Organizer}	${k}
		${log}=	Get From List	${logins}	${k}
		${email}=	Get Item	${log}	login
		@{list}=	Get From Dictionary		${VariableDict}		${email}
		${bool}=	Run Keyword And Return Status	Should Be Empty		${list}
		Continue For Loop If	${bool}
		Open Calendar	${log}
		Create And Save Events From List	${list}
		Close Browser
	END

*** Keywords ***
Create And Save Events From List
	[Documentation]	Create an event with all the info already well formated
	[Arguments]		${list}
	${is ampm}=	Run Keyword And Return Status	Page Should Contain	12:00 PM
	Set Global Variable	${is ampm}
	FOR    ${event}    IN	@{list}
		${Date}=	Get From Dictionary		${event}	date
		${Name}=	Get From Dictionary		${event}	eventName
		${BegHour}=	Get From Dictionary		${event}	begHour
		${EndHour}=	Get From Dictionary		${event}	endHour
		Create Formated Event	${Date}		${Name}		${BegHour}	${EndHour}
	END

Set Formated Hour
	[Documentation]	Set the given hour for the event
	[Arguments]	${BegHour}	${EndHour}

	Clear Hour	[ng-model='ctrl.start']:last
	Input Text	jquery:[ng-model='ctrl.start']:last	${BegHour}
	Click Element	jquery:.modal-title
	
	Clear Hour	[ng-model='ctrl.end']:last
	Input Text	jquery:[ng-model='ctrl.end']:last	${EndHour}
	Click Element	jquery:.modal-title

Create Formated Event
	[Arguments]		${Date}		${Name}		${BegHour}	${EndHour}
	Click Button	jquery:.waves-effect.waves-light.btn-accent
	Wait Until Page Contains	No repetition	timeout=10
	Sleep	0.1
	Input Text	jquery:.event-form .input.title	${Name}
	Set Formated Hour  ${BegHour}  ${EndHour}
	Input Text	jquery:.input.form-control.date:first	${Date}
	${alarm}=	Evaluate	str(random.randint(2,7))
	Select From List By Value	jquery:[ng-model="ctrl.trigger"]	${alarm}
	Input Text	jquery:[ng-model='editedEvent.location']	Paris, France
	Click Button	jquery:button.btn.btn-primary.save