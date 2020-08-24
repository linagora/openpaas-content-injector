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
${YEAR}		2020
${MONTH}	7
${DAY}		30
${LANGUAGE}	English
#intern variables
${meridiem}	AM

*** Tasks ***
Set Variables
	Set Global Variable	${PATH NAME}	${PATH}/Events/${LANGUAGE}_Name_events
	Set Global Variable	${PATH LOGINS}	${PATH}/Config/logins
	Parse A File	${PATH}/Config/sitesUrl
	${LOGIN OP}=	Get Item	Calendar	url
	Set Global Variable		${LOGIN OP}

Set One Month Of Events
	Reinitialize Parser
	Parse A File	${PATH LOGINS}
    ${logins}=	Get Sections List
	${Size}=	Evaluate	len(${logins})
	FOR	${k}	IN RANGE	${Size}
		Set Global Variable	${Organizer}	${k}
		${log}=	Get From List	${logins}	${k}
		Open Calendar	${log}
		Create And Save Events
		Close Browser
	END

*** Keywords ***
Create And Save Events
	[Documentation]	Create all the events of the month taken as an input
	${number of days}=	Evaluate	calendar.monthrange(${YEAR}, ${MONTH})[1]
	${is ampm}=	Run Keyword And Return Status	Page Should Contain	12:00 PM
	Set Global Variable	${is ampm}
	FOR    ${day}    IN RANGE    ${DAY}	${number of days}+1
		Continue For Loop If	datetime.date(${YEAR}, ${MONTH}, ${day}).weekday()>4
		Create Events Of A Day	${day}	${MONTH}
	END

Set Date
	[Arguments]	${day}	${month}
	${raw Date}=	Evaluate	datetime.datetime(${YEAR},${month},${day})
	${Date}=	Convert Date	${raw Date}	result_format=%a %Y/%m/%d
	Input Text	jquery:${event_date_locator}	${Date}


Get AMPM Hour
	[Documentation]	Convert a 24h format in 12h (considering only day time)
	[Arguments]	${hour}
	${hour prime}=	Evaluate	${hour}-12
	Run Keyword If	${hour}<12	Set Global Variable	${meridiem}	AM
	Run Keyword If	${hour}>=12	Set Global Variable	${meridiem}	PM
	Run Keyword If	${hour}>12	Set Local Variable	${hour}	${hour prime}
	[Return]	${hour}

Get Hour
	[Arguments]	${hour}						#format 13.75
	${ampm hour}=	Get AMPM Hour	${hour}				#format 1.75 (PM)
	${real hour}=	Set Variable If	${is ampm}	${ampm hour}	${hour}
	${real hour}=	Convert Time	${real hour} hours	timer	#format 1:45 (PM) or 13:45
	${real hour}=	Get Substring	${real hour}	0	5
	${input hour}=	Set Variable If	${is ampm}	${real hour} ${meridiem}	${real hour}
	[Return]	${input hour}

Set Hour
	[Documentation]	Set the hour of the event
	[Arguments]	${possible debut hour}
	${hour of beg}=	Evaluate	random.randint(${possible debut hour},${possible debut hour}+1)
	${quarter of beg}=	Evaluate	random.randint(0,3)/4

	${beginning}=	Evaluate	${hour of beg}+${quarter of beg}
	${input hour}=	Get Hour	${beginning}

	Clear Hour	${first_hour_locator}
	Input Text	jquery:${first_hour_locator}	${input hour}
	Click Element	jquery:${modal_title_locator}
	
	${duration}=	Evaluate	random.randint(3,10)/4

	${end}=		Evaluate	${beginning}+${duration}
	${input hour}=	Get Hour	${end}

	Clear Hour	${end_hour_locator}
	Input Text	jquery:${end_hour_locator}	${input hour}
	Click Element	jquery:${modal_title_locator}
	[Return]	${end}

Create Event
	Click Button	jquery:${creation_button}
	Wait Until Page Contains	No repetition	timeout=10
	Sleep	0.1
	${event}=	Get Random Field In File	${PATH NAME}
	${name}	${description}	@{attribute}=	Split String	${event}	|

	Input Text	jquery:${event_title_locator}	${name}
	Input Text	jquery:${event_descripion_locator}	${description}
	[Return]	${attribute}

Set Date and Hour of Event
	[Documentation]	Set the date and the hour of the event
	[Arguments]	${day}	${month}	${hour}	${attribute}
	${next hour}=	Set Hour	${hour}
	${bool}=	Run Keyword And Return Status	Should Contain	${attribute}	evening
	Run Keyword If	${bool}	Set Hour	19
	${bool}=	Run Keyword And Return Status	Should Contain	${attribute}	lunch
	Run Keyword If	${bool}	Set Hour	12
	${next hour}=	Evaluate	int(math.ceil(${next hour}))
	Set Date	${day}	${month}
	[Return]	${next hour}

Set Details
	[Documentation]	Set details of the event
	[Arguments]	${attribute}
	Input Text	jquery:${event_location_locator}	Paris, France
	${num}=		Evaluate	-1
	${bool}=	Run Keyword And Return Status	Should Contain	${attribute}	many
	Run Keyword If	${bool}	Set Local Variable	${num}	5
	@{email names}=	Get x Random Field In File	${Organizer}	${num}
	${bool}=	Run Keyword And Return Status	Should Contain	${attribute}	alone
	Run Keyword If	${bool}	Set Local Variable	${email names}	
	Input Text	jquery:${email_locator}	${login},
	FOR	${email name}	IN	@{email names}
		Input Text	jquery:${email_locator}	${email name},
	END
	${bool}=	Run Keyword And Return Status	Should Contain	${attribute}	weekly
	Run Keyword If	${bool}	Select From List By Value	jquery:${frequence_locator}	2
	${bool}=	Run Keyword And Return Status	Should Contain	${attribute}	allday
	Run Keyword If	${bool}	Click Element	jquery:${full_day_locator}
	${alarm}=	Evaluate	str(random.randint(2,7))
	Select From List By Value	jquery:${alarm_locator}	${alarm}

Create Events Of A Day
	[Documentation]	Create all (3) events in the given day
	[Arguments]	${day}	${month}
	${hour}=	Evaluate	9
	FOR	${i}	IN RANGE	3
		${attribute}=	Create Event
		${hour}=	Set Date and Hour of Event	${day}	${month}	${hour}	${attribute}
		Set Details	${attribute}
		Save Event
	END