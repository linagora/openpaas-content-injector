*** Settings ***
Documentation	Example
Library         OperatingSystem
Library		  	SeleniumLibrary
Library		 	String
Library		  	Collections
Library			ParsingForRf.py
Resource		Ressources.robot

*** Variables ***
#can be set in cmd line
${LOGIN URL}	https://web_adress_of_twake

${PATH}		../RawData
${LANGUAGE}	English			#can either be Russian or English, set `--variable LANGUAGE:Russian` in the options of the robot call
${NB OF MESSAGES}	${3}

${ALIAS USER}	${1}
${COMPANY NAME}	Test

*** Tasks ***
Set Variables
	Parse A File	${PATH}/Config/sitesUrl
	${LOGIN URL}=	Get Item	Twake	url
	Set Global Variable		${LOGIN URL}
	${COMPANY NAME}=	Get Item	Twake	company_name
	Set Global Variable		${COMPANY NAME}

Open Twake
	[Tags]	all
	[Documentation]	Open firefox and input credentials
	Reinitialize Parser
	Parse A File	${PATH}/Config/loginTwake
	@{logins}=	Get Sections List
	Set Global Variable	${logins}
	${numberUsers}=	Evaluate	len(${logins})
	Set Global Variable	${numberUsers}
	FOR	${name}	IN	@{logins}
		Open Browser To Login Page	${LOGIN URL}	username
		${log}=		Get Item	${name}	login
		${password}=	Get Item	${name}	password
		Input Twake Credentials	${log}	${password}
		Wait Until Element Is Visible	jquery:textarea.input
		Change Company	${COMPANY NAME}
	END

Write Dialogs In General And Random Channels
	[Documentation]	Write the desired number of dialogs in default channels
	[Tags]	all
	Create Workspace
	FOR	${i}	IN RANGE	1	6
		Switch Browser	${i}
		Select Created Channel	first
	END
	Fill One Channel
	FOR	${i}	IN RANGE	1	6
		Switch Browser	${i}
		Select Created Channel	last
	END
	Fill One Channel
	

Write Dialogs In Other Channels
	[Documentation]	Write the desired number of dialogs in different chanels
	[Tags]	all
	
	${Channel File}=	Get File	${PATH}/Twake/${LANGUAGE}_ChannelTitle
	@{Channels}=	Split To Lines	${Channel File}
	FOR	${Channel}	IN	@{Channels}
		Create And Select Channel	${Channel}
		Fill One Channel
	END

*** Keywords ***
Input Twake Credentials
	[Arguments]	${username}	${password}
	Input Text	username	${username}
	Input Password	password	${password}
	Click Button	login_btn

Change Company
	[Documentation]	Change to the given company
	[Arguments]	${companyName}
	Wait Until Element Is Visible	jquery:.current_company_logo
	${shortName}=	Get Substring	${companyName}	0	6
	${todo}=	Run Keyword And Return Status	Page Should Not Contain	${shortName}
	Run Keyword If	${todo}	Click Element	jquery:.current_company_logo
	Run Keyword If	${todo}	Click Element	jquery:div:contains(${COMPANY NAME}):last
	Wait Until Element Is Visible	jquery:textarea.input

Create Workspace
	[Documentation]	Create a new workspace in the current company
	Switch Browser	${1}
	Wait Until Element Is Visible	jquery:.workspace.workspaceadd
	Click Element	jquery:.workspace.workspaceadd
	${workspaceName}=	Generate Random String
	Input Text	jquery:.input	${workspaceName}
	Click Button	jquery:.button
	FOR	${index}	IN RANGE	1	len(@{logins})
		${log}=		Get From List	${logins}	${index}
		@{current login}=	Split String	${log}	|
		Input Text	jquery:.input:last	${current login}[0]
	END
	Click Button	jquery:.button
	Wait Until Element Is Visible	jquery:textarea.input	timeout=10
	FOR	${i}	IN RANGE	2	6
		Switch Browser	${i}
		Change Channel	${workspaceName}
	END

Change Channel
	[Arguments]	${Channel}
	Click Element	jquery:div:contains('${Channel}'):last

Select Created Channel
	[Arguments]	${position}	#first or last
	Click Element	jquery:.fade_in.extra-margin:${position}

Create And Select Channel
	[Documentation]	Create a new channel
	[Arguments]	${CHANNEL}
	FOR	${i}	IN RANGE	1	6
		Switch Browser	${i}
		Run Keyword If	$i==1	Create Channel	${CHANNEL}
		Run Keyword If	$i==1	Wait Until Element Is Visible	jquery:div:contains('${CHANNEL}')
		Change Channel	${CHANNEL}
	END

Fill One Channel
	FOR	${j}	IN RANGE	${NB OF MESSAGES}
		${nb}	${File}=	Choose a Dialog
		Write The Dialog	${nb}	${File}
	END

Open Answer
	[Arguments]	${user}
	Switch Browser	${user}
	Reload Page
	Wait Until Element Is Visible	jquery:.action_link.add_response:last
	Click Element	jquery:.action_link.add_response:last

Send Answer
	[Arguments]	${text}	${user}
	Switch Browser	${user}
	Input Text	jquery:.messages_flex .full_width	${text}
	Click Button	jquery:button.button.small.right-margin

Send Text from
	[Arguments]	${text}	${user}
	Switch Browser	${user}
	Input Text	jquery:textarea.input:last	${text}
	Click Button	jquery:button.button.medium.primary

Create Channel
	[Documentation]	Create a new channel considering it doesn't exist already
	[Arguments]	${Channel}
	Click element	jquery:.uil-plus-circle:first
	Input Text	jquery:input.full_width.medium	${Channel}
	Click Button	jquery:button.button.small.primary-text
	Click Button	jquery:button.button.small.primary

Choose A Dialog
	[Documentation]	Select a random dialog (the first line of it) from the file in the language depending on the global variable
	${Conv_ids}=	Get File	${PATH}/Twake/${LANGUAGE}_dialogues.txt
	${Size}=	Get Line Count	${Conv_ids}
	${random} = 	Evaluate 	random.randint(0, $Size-1)
	${Conv_line}=	Get Line	${Conv_ids}	${random}
	FOR    ${i}    IN RANGE    99
   	   	Exit For Loop If    "${Conv_line}" == '${EMPTY}'
		${random}=	Evaluate	${random}-1
		${Conv_line}=	Get Line	${Conv_ids}	${random}
    END
	[Return]	${random}	${Conv_ids}

Write The Dialog
	[Arguments]	${nb of line}	${Conv_ids}
	${nb of line}=	Evaluate	1+${nb of line}
	${Conv_line}=	Get Line	${Conv_ids}	${nb of line}
	${first}=	Evaluate	random.randint(1,${numberUsers})
	${second}=	Evaluate	random.randint(1,${numberUsers})
	${bis}=		Evaluate	(${second}+1)%${numberUsers}+1
	Run Keyword If	${first}==${second}	Set Local Variable	${second}	${bis}
	${ALIAS USER}=	Evaluate	str(${first})
	FOR	${i}    IN RANGE	99
		Run Keyword If	$i==0	Send Text from	${Conv_line}	${ALIAS USER}
		Run Keyword Unless	$i==0	Open Answer	${ALIAS USER}
		Run Keyword Unless	$i==0	Send Answer	${Conv_line}	${ALIAS USER}
		${ALIAS USER}=	Evaluate	str(${first}+${second}-${ALIAS USER})
		${nb of line}=	Evaluate	1+${nb of line}
		${Conv_line}=	Get Line	${Conv_ids}	${nb of line}
   		Exit For Loop If    "${Conv_line}" == '${EMPTY}'
	END

