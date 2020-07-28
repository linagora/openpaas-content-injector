*** Settings ***
Documentation	Create an event in OpenPaas
Library         OperatingSystem
Library		  	SeleniumLibrary
Library		  	String
Library		  	Collections
Library    	  	DateTime
Resource		Ressources.robot

*** Variables ***
#can/has to be changed in command line
${LOGIN OP}	https://an_open_pass_site/#/calendar

${PATH}		../RawData/


*** Tasks ***
Set Variables
	${FileUrl}=	Get File	${PATH}/Config/sitesUrl
	Set Global Variable	${PATH LOGINS}	${PATH}/Config/logins
	${LOGIN OP}=	Get Line	${FileUrl}	0
	Set Global Variable		${LOGIN OP}

Create The Events In The List
	${Filelogin}=	Get File	${PATH LOGINS}
	${Size}=	Get Line Count	${Filelogin}
	FOR	${k}	IN RANGE	${Size}
		Set Global Variable	${Organizer}	${k}
		${log}=	Get Line	${Filelogin}	${Organizer}
		@{cred}=	Split String	${log}	|
		@{list}=	Get From Dictionary		${VariableDict}		${cred}[0]
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