# Twake

## ChannelTitle
This file contains the titles given to the channels added in the Twake workspace. You can add and remove them at will.

## Dialogues
This files contains the database of the dialogs injected in Twake. A dialog is always beetween two people, for convenience. Each line corresponds to a replica.

Each dialog is separated from others by a linebreak, so to add a dialog you just have to add it at the end of the file, with a mandatory linebreak after it.

## Tasks
The English and Russian folders work the same way, the files use an INI structure. In Twake, you can manage tasks in boards, in each board you can create lists of tasks (for example, `To do`, `Done`).

A file in these folders describes a list of task. It must be organized this way:
```
[DEFAULT]
board_name : Main Board
task_list_name : To Do

[First]
name : Explain how Twake works to the team
tags : Urgent
subtasks : Collaboration,Tasks Management
assignees : yes

[Second]
name : Star the Twake repository on Github
tags : Urgent
subtasks : https://github.com/TwakeApp/Twake
assignees : no
```

* The `[DEFAULT]` section is mandatory and contains the name of the board where the list will appear and its name. If the board does not exist yet, it will be created by the script, otherwise the list will be added to the existent board.
* Others sections describe a task in the given list, you can write as many as you want. They have the attributes
  * name
  * tags : you can put no or several tags, separated by commas (with no leading or trailing spaces)
  * subtasks : as for tags, you can write no or several subtasks
  * assignees : can take `yes` or `no` values depending on whether you want assignees or not

> Note that the section title (apart from the `DEFAULT` section) and the file name can be whatever you want, as they aren't used.