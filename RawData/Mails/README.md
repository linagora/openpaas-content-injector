## Mails

A file in this folder is a mail, already written in `html`. The file is formatted when processed in the scripts, in order to personnalize the names of the receiver, the sender,...
> Warning: Even if written in html, the file title must have no extension

The name of the file gives the title of the email, as well as details about it.

For example, the file `Needs Assessment_attach_Needs Assessment Form.pdf_` is :
```html
<h5>Hey {receiver},</h5><br>
<p>I received your note from Bob Lebowsky.  I am the ENA Staffing Coordinator and need for you to fill out the attached Needs Assessment form before I can send you any resumes.  Also, would you be interested in the new class?  Analysts start with the business units on Aug. 3rd and Assoc. start on Aug. 28th.  We are starting to place the Associates and would like to see if you are interested.  Please let me know.</p>
<br>
<p>Once I receive the Needs Assessment back (and you let me know if you can wait a month,) I will be happy to pull a couple of resumes for your review.  If you have any questions, please let me know. Thanks.</p>
<br> <div class="openpaas-signature"> -- <br>
 <p>{sender}<br>email: <a href="mailto:{sender_mail}">{sender_mail}</a></p></div>
```

Here, the mail title will be `Needs Assessment`, it has an attachments, which is the file [Needs Assement Form](../Linshare/Files/English/Needs%20Assessment%20Form.pdf).

The formating depends on the details given in the email title. You can always use `{receiver}`, `{sender}` and `{sender_mail}`. They will be replaced in the sent email by the receiver *first* name, the sender *full* name and the sender email.

The file title is a string, each fields are separated with an `_`. The option you can add is one of the following:
* copy: when the mail is supposed to have a copy. You can use in the html encoding `{in_copy}` which will be replaced by the full name of the receiver in copy.
* many: when the mail is supposed to be sent to many people (for example an entire team). In this case, the file should not contain the `{receiver}` paramater, to be logical.
* attach: when the mail has an attachment. You can add the title of the attachment as a third field - as in the example - if you want a specific file of the `Linshare/Files` folder to be used.  Otherwise, a random file will be sent.
> Be aware to add an `_` at the end of the attachment name, in order to leave the mail file name without extension
* event: when the mail is related to an event. It will add this event in the Calendar. If you want to mention the exact date of the event in the mail you can use `{event_date}`. In this case,you must have 3 additional fields after the `event`, as in: `Absence at the Friday meeting_event_Eye doctor_fr_09am-10am`. The first of the remaining fields will be the name of the event to add in the calendar, the second its english weekday abreviated in two letters, the last one is the hour of the beginning and the end of the event. The hour must match the format `HH*m-HH*m` (replace the `*` by `a` or `p`), as in the example.

> Explanation: the idea is that in the email, an event happening `next Friday` is mentionned, so this event will be added on the Friday following the date of sending of the email.