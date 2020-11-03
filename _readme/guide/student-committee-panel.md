# Design Guide - Student Committee Panel

Student committee panel is a panel where only active student committee members can access. This panel includes 2 tabs.

## Rendering the Button

The button to access this panel reside in the navigator bar. Call this API to check if the current logged-in user is an active member.

`GET api/user/user/me`

A field `is_student_committee` is expected. If is `true`, then render the button.

## Assigning Advisors Tab

In this tab, student committee members are able to assign lecturers as an advisor of clubs and events (excluding community events).

### List Advisories

First of all, list all advisories by calling these 2 APIs. Separate the active advisories and non-active advisories out of each other.

`GET api/membership/advisory?is_active=1`

`GET api/membership/advisory?is_active=0`

### Add Advisory

Implements a button that let student committee members add the advisory to the club or the event. After clicking the button, the pop-up form will appear.

In the form, the student committee member can choose the lecturer as an advisor, a filter of choice is required. Call this API to implement this as choices for advisor of the advisory.

`GET api/user/user?user_group=lecturer`

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

### Delete Advisory

Advisories can be deleted by student committee members, this feature is added in order to allow student committee members to fix their mistakes in adding advisories. Simply render the delete button next to each advisory object, and call this API upon the button is clicked.

`DELETE api/membership/advisory/{int}`

## Approval Requests Tab

In this tab, student committee members are able to approve clubs and events that are requested to be approved. Unofficial clubs can become official clubs, unapproved events can become approved events.

### Pending Approval Requests

First, list all pending approval requests. Call this API to list them.

`GET api/membership/approval-request?status=W`

### Approve Approval Request

These approval requests also need 2 buttons each, approved and decline buttons. Call one of these two APIs upon the user clicked approve button.

`PUT api/membership/approval-request/{int}`

`PATCH api/membership/approval-request/{int}`

```json
{
    "status": "A"
}
```

### Decline Approval Request

On the other hand, call one of these two APIs upon the user clicked decline button.

`PUT api/membership/approval-request/{int}`

`PATCH api/membership/approval-request/{int}`

```json
{
    "status": "D"
}
```

### Approved and Declined Approval Requests

After listing all pending approval request, add a separator for approval requests that were already either approved or declined. Call these two APIs, concatenate them, then sort them by `created_at` or `id` at the descending order.

`GET api/membership/approval-request?status=A`

`GET api/membership/approval-request?status=D`
