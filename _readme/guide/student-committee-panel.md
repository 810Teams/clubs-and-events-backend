# Design Guide - Student Committee Panel

Student committee panel is a panel where only active student committee members can access.

## Rendering the Button

The button to access this panel reside in the navigator bar. Call this API to check if the current logged-in user is an active member.

`GET api/user/user/me`

A field `is_student_committee` is expected. If is `true`, then render the button.

## Assigning Advisors Section

Student committee members are able to assign lecturers as an advisor of clubs and events (excluding community events).

### List Advisories

First of all, list all advisories by calling these 2 APIs. Separate the active advisories and non-active advisories out of each other.

`GET api/membership/advisory?is_active=1`

`GET api/membership/advisory?is_active=0`

### Add Advisory

Implements a button that let student committee members add the advisory to the club or the event. After clicking the button, the pop-up form will appear.

In the form, the student committee member can choose the lecturer as an advisor, a filter of choice is required. Call this API to implement this as choices for advisor of the advisory.

`GET api/user/user?is_lecturer=1`

As well as the community choices. The community is needed to be either a club or an event. Call these 2 APIs and concatenate them, then implement this as choices for community of the advisory.

`GET api/community/club`

`GET api/community/event`

After filling the form, call this API to add the advisory.

`POST api/membership/advisory`

```json
{
    "advisor": "int",
    "community": "int",
    "start_date": "date",
    "end_date": "date"
}
```

Please note that the club or the event can hold more than 1 advisor at a time, but if any time-overlapping advisory is attempted to be added, a status `400` will be returned.

## Approval Section

> To be written
