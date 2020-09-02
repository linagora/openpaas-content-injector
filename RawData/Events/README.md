## Events

The events files contain only example of event titles. Each line corresponds to one event, with 2 or more fields separated with a `|`.

A line should looks like:

```
Meeting at the Embassy of France|The Embassador seems eager to know us better|evening
```

The first is the title of the event, the second its description. The remaining fields give detail about the event and they are optionnal.
> Note: You can leave the second field blank as in `Title of the event|` or `Title of the event||weekly` but it still is mandatory.

The last fields may be in the followings. Of course, giving contradictory details will have unintended consequences.
* weekly: for a weekly event
* allday: for an event all day long
* lunch: for an event which should be planned at lunch time
* evening: for an event which should planned during the evening
* alone: for an event without any attendee
* many: for an event with many attendees