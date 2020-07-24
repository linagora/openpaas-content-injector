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
	[Documentation]	Select random lines in a file
	[Arguments]	${PATH}	${Exclude}=-1
	${Name_ids}=	Get File	${PATH}
	${Size}=	Get Line Count	${Name_ids}
	${number}=	Evaluate 	random.randint(1, $Size)
	@{usedLines}=	Create List	${Exclude}
	@{lines}=	Create List
	FOR	${i}	IN RANGE	99
		${random} = 	Evaluate 	random.randint(0, $Size-1)
		${boolean}=	Run Keyword And Return Status	List Should Not Contain Value	${usedLines}	${random}
		${line}=	Get Line	${Name_ids}	${random}
		Run Keyword If	${boolean}	Append To List	${lines}	${line}
		Run Keyword If	${boolean}	Append To List	${usedLines}	${random}
		Exit For Loop If	len(${lines})==${number}
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
	
