*** Variables ***
#locator variables
# For Calendar:
${event_date_locator}	.input.form-control.date:first
${first_hour_locator}	[ng-model='ctrl.start']:last
${end_hour_locator}		[ng-model='ctrl.end']:last
${modal_title_locator}	.modal-title
${creation_button}		.waves-effect.waves-light.btn-accent
${event_title_locator}	.event-form .input.title
${event_descripion_locator}	[ng-model='editedEvent.description']
${event_location_locator}	[ng-model='editedEvent.location']
${email_locator}		[type='email']:last
${frequence_locator}	[ng-model="vm.freq"]
${full_day_locator}		[ng-model="ctrl.full24HoursDay"]
${alarm_locator}		[ng-model="ctrl.trigger"]
${save_button_locator}	button.btn.btn-primary.save
${last_button}		.waves-effect:last
${close_button}		.close-button
${credentials_button}	button.btn.btn-success
${ok_button_hour}	.btn.btn-sm.btn-default.btn-block.clockpicker-button:last

#For Twake:
${textarea_locator}		textarea.input
${company_logo}			.current_company_logo
${add_workspace_locator}	.workspace.workspaceadd
${input_locator}		.input
${button_locator}		.button
${select_channel_locator}	.fade_in.extra-margin:
${open_answer_locator}		.action_link.add_response:last
${message_flex_locator}		.messages_flex .full_width
${send_answer_locator}		button.button.small.right-margin
${send_text_locator}		button.button.medium.primary
${plus_locator}				.uil-plus-circle:first
${channel_input_locator}	input.full_width.medium
${create_channel_locator}	button.button.small.primary-text
${confirm_channel_locator}	button.button.small.primary
${task_icon}				.icon-unicon.uil-check-square.undefined
${dots_first_board}			.options:first
${suppress_board}			.menu.error
${suppress_board_confirm}	.button.medium:last
${create_board_plus}		.MuiSvgIcon-root.m-icon-small:last
${create_board_confirm}		.button.small
${create_board_panel}		.menu-list.as_frame.skew_in_right
${add_tasklist}				.rounded-btn.list_add
${add_task}					.add_task.unselected:last
${add_all_button}			.button.small.primary-text:last
${add_tag}					.button.small.secondary-text:first
${add_subtask}				.checklist .button.small.secondary-text
${text_input}				.input.full_width
${all_boards}				.app_back_btn
${board_name_locator}		.board_frame.fade_in
${confirm_tag}				.menu.is_selected

*** Keywords ***
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
	${number}=	Set Variable If	${numberp}!=-1	${numberp}	${number}
	@{names}=	Evaluate	random.sample(${logins}, min(${number}, ${Size}-1))
	@{lines}=	Create List
	FOR	${attendee}	IN	@{names}
		${line}=	Get Item	${attendee}	mail
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
	Click Button	jquery:${save_button_locator}
	Sleep	0.1
	Run Keyword And Continue On Failure	Click Button	jquery:${last_button}
	Sleep	0.1
	Run Keyword And Continue On Failure	Click Button	jquery:${save_button_locator}
	Run Keyword And Continue On Failure	Click Button	jquery:${close_button}
	Reload Page
	Wait Until Element Is Enabled	jquery:${creation_button}
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
	Wait Until Element Is Visible	jquery:${creation_button}

Open Browser To Login Page
	[Arguments]		${LOGIN PAGE}	${wait}
	Open Browser	${LOGIN PAGE}
	Wait Until Element Is Visible	${wait}

Input Credentials
	[Arguments]	${username}	${password}
	Input Text	user	${username}
	Input Password	password	${password}
	Click Button    jquery:${credentials_button}

Clear Hour
	[Arguments]	${query}
	Click Element	jquery:${query}
	Press Keys	None	CTRL+A
	Press Keys	None	DELETE