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
	Set Global Variable	${PATH LOGINS}	${PATH}/Config/loginOpenPaas
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

	Clear Hour	${first_hour_locator}
	Input Text	jquery:${first_hour_locator}	${BegHour}
	Click Element	jquery:${modal_title_locator}
	
	Clear Hour	${end_hour_locator}
	Input Text	jquery:${end_hour_locator}	${EndHour}
	Click Element	jquery:${modal_title_locator}

Create Formated Event
	[Arguments]		${Date}		${Name}		${BegHour}	${EndHour}
	Click Button	jquery:${creation_button}
	Wait Until Page Contains	No repetition	timeout=10
	Sleep	0.1
	Input Text	jquery:${event_title_locator}	${Name}
	Set Formated Hour  ${BegHour}  ${EndHour}
	Input Text	jquery:${event_date_locator}	${Date}
	${alarm}=	Evaluate	str(random.randint(2,7))
	Select From List By Value	jquery:${alarm_locator}	${alarm}
	Input Text	jquery:${event_location_locator}	Paris, France
	Click Button	jquery:${save_button_locator}