***Keywords***
Get Random Field In File
	[Documentation]	Select a random line in a file
	[Arguments]	${PATH}	${Exclude}=-1
	${Name_ids}=	Get File	${PATH}
	${Size}=	Get Line Count	${Name_ids}
	FOR	${i}	IN RANGE	99
		${random} = 	Evaluate 	random.randint(0, $Size-1)
		Exit For Loop If	${random}!=${Exclude}
	END
	${line}=	Get Line	${Name_ids}	${random}
	[Return]	${line}


Get x Random Field In File
	[Documentation]	Select random lines in the currently parsed file
	[Arguments]	${Exclude}=-1	${numberp}=-1
	${logins}=	Get Sections List
	Run Keyword If	${Exclude}!=-1	Evaluate	${logins}.pop(${Exclude})
	${Size}=	Evaluate	len(${logins})
	${number}=	Evaluate 	random.randint(1, $Size//2 +1)
	Run Keyword If	${numberp}!=-1	Set Local Variable	${number}	${numberp}
	@{linesNumbers}=	Evaluate	random.sample(${logins}, min(${number}, ${Size}-1))
	@{lines}=	Create List
	FOR	${lineNumber}	IN	@{linesNumbers}
		${line}=	Get Item	${logins}[${lineNumber}]	mail
		Append To List	${lines}	${line}
	END
	[Return]	${lines}


Change x Number In Date
	[Documentation]	Change one number in both date fields, x takes the values 1,2,4,5 corresponding to 12/45=MM/DD
	[Arguments]	${x}	${target}
	#Click Element	jquery:.input.form-control.date:first
	#Execute Javascript	$(".input.form-control.date:first")[0].setSelectionRange(8+${x}, 9+${x});
	Press Keys	None	${target}

Backup
	${month1}=	Evaluate	str(${month}//10)
	${month2}=	Evaluate	str(${month}%10)
	${day1}=	Evaluate	str(${day}//10)
	${day2}=	Evaluate	str(${day}%10)
	
	${current}=	Get Current Date	result_format=datetime
	Run Keyword If	${current.month}==10	Change x Number In Date	2	1

	Run Keyword If	${current.month}<10 and ${month}!=10	Change x Number In Date	2	${month2}
	Run Keyword If	${current.month}<10 and ${month}==10	Change x Number In Date	2	1

	Change x Number In Date	1	${month1}

	Run Keyword If	${current.month}>=10	Change x Number In Date	2	${month2}
	Run Keyword If	${month}==10	Change x Number In Date	2	0

	Run Keyword If	${current.day}>29	Change x Number In Date	4	2
	Run Keyword If	${current.day}>29	Change x Number In Date	5	9
	
	Run Keyword If	${day}%10!=0 or ${current.day}>9	Change x Number In Date	5	${day2}
	Change x Number In Date	4	${day1}
	Run Keyword If	${day}%10==0 and ${current.day}<10	Change x Number In Date	5	${day2}
	
Save Event
	Click Button	jquery:button.btn.btn-primary.save
	Sleep	0.1
	Run Keyword And Continue On Failure	Click Button	jquery:.waves-effect:last
	Sleep	0.1
	Run Keyword And Continue On Failure	Click Button	jquery:button.btn.btn-primary.save
	Run Keyword And Continue On Failure	Click Button	jquery:.close-button
	Reload Page
	Wait Until Element Is Enabled	jquery:.waves-effect.waves-light.btn-accent
	Sleep	0.1

Open Calendar
	[Documentation]	Open firefox and input credentials in OP
	[Arguments]	${log}
	Open Browser To Login Page	${LOGIN OP}		user
	${name}=	Get Item	${log}	mail
	${password}=	Get Item	${log}	password
	Set Global Variable	${login}	${name}
	Input Credentials	${name}	${password}
	Wait Until Page Contains	Spam
	Go To	${LOGIN OP}
	Wait Until Element Is Visible	jquery:.waves-effect.waves-light.btn-accent

Open Browser To Login Page
	[Arguments]		${LOGIN PAGE}	${wait}
	Open Browser	${LOGIN PAGE}
	Wait Until Element Is Visible	${wait}

Input Credentials
	[Arguments]	${username}	${password}
	Input Text	user	${username}
	Input Password	password	${password}
	Click Button    jquery:button.btn.btn-success

Clear Hour
	[Arguments]	${query}
	Click Element	jquery:${query}
	Press Keys	None	CTRL+A
	Press Keys	None	DELETE