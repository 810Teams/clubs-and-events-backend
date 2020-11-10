# Design Guide - Community Page (Header)

## Header

By visiting any community page, simply it means that the client must call one of these 4 APIs to retrieve the community's data. Make sure to display all important information.

`GET api/community/club/{int}`

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

`GET api/community/lab/{int}`

### Rendering the Request Button

Request button simply means request to join button. Upon calling one of the APIs above, look for the field `meta.request_ability.is_able_to_send_request`, the structure should be something like this.

```json
{
    "meta": {
        "request_ability": {
            "is_able_to_send_request": false,
            "code": "restricted",
            "message": "Only students are able to join the club."
        }
    }
}
```

If the field `is_able_to_send_request` is `true`, simply render the button, but if is `false`, follow these steps based on the field `code`

#### Able to send request

By clicking the request button, this API must be called.

`POST api/membership/request`

```json
{
    "community": "int"
}
```

The `"int"` is the ID of the community user requested to join, must be auto.

#### Code 1: restricted

If the field `code` is `"restricted"`, simply render the button useless, making it gray, and unclickable.

Furthermore, when the user hovers over the disabled button, display the message from the field `message`.

#### Code 2: already_member

If the field `code` is `"already_member"`, simply render the button labeled as `"Joined"`, but unclickable, or clicking does nothing.

#### Code 3: pending_invitation

If the field `code` is `"pending_invitation"`, render the [accept and decline invitation](#accept-or-decline-invitation) buttons instead.

Call this API to fetch the ID of the invitation for further usage.

`GET api/membership/invitation?invitee={int}&community={int}&status=W`

If the user clicked the accept invitation button, use one of these two APIs.

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "A"
}
```

If the user clicked the decline invitation button, use one of these two APIs.

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "D"
}
```

#### Code 4: pending_request

If the field `code` is `"pending_request"`, render the cancel request button instead.

Call this API to fetch the ID of the request for further usage.

`GET api/membership/request?user={int}&community={int}&status=W`

If the user clicked the cancel request button, use this API. Deleting a pending join request is equivalent to cancelling the join request.

`DELETE api/membership/request/{int}`

The `{int}` is the ID of the request, can be obtained by calling this API, and retrieve the ID of the first object in the list. The length of the list should never exceed 1 from begin.

### Get Available Actions

Upon calling one of the APIs above in the [heading](#heading) section, a field `available_actions` is expected, then check if the list contains these values.

|Code|Action|
|:-:|:-|
|"send-approval-request"|Renders a button that let the current user send approval request to student committee members.|
|"cancel-approval-request"|Renders a button that let the current user cancel the approval request sent to student committee members.|
|"edit"|Renders a button that let the current user edit the community.|
|"delete"|Renders a button that let the current user delete the community separately in the [edit page](edit-page.md).|
|"active"|Renders a button that revert user from being retired to active.|
|"retire"|Renders a button that set the current user's membership status to retired.|
|"leave"|Renders a button that let the current user leaves the community.|
|"comment"|Renders a button that let the current user writes comment in the comments tab.|

These are actions, all should be placed in the same pop-up menu button, unlike request button which is an individual button. This is to prevent accidental action performings.

For the action code `edit` and `delete`, render the edit community button, and visit the [edit page](edit-page.md) for the further guide.

### Send Approval Request

Upon the leader of the unofficial club or unapproved event clicked the "Send Approval Request", display a form. After the user filled the form, and confirmed. Call this API to send the approval request.

`POST api/membership/approval-request`

```json
{
    "community": "int",
    "message": "string",
    "attached_file": "file"
}
```

The community must be auto.

### Cancel Approval Request

If this action appears, meaning the club or the event is having a pending approval request. Retrieve the approval request by calling this API.

`GET api/membership/approval-request?community={int}`

Upon the leader of the unofficial club or unapproved event clicked the "Cancel Approval Request", display a confirmation dialog, if the user confirmed, call this API to cancel the approval request.

`DELETE api/membership/approval-request/{int}`

### Retiring from Community

The membership ID can be retrieved from the community object from calling one of the APIs as described in the [heading](#heading) section.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "R"
}
```

### Back in Duty to Community

The membership ID can be retrieved from the community object from calling one of the APIs as described in the [heading](#heading) section.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "A"
}
```

### Leaving Community

The membership ID can be retrieved from the community object from calling one of the APIs as described in the [heading](#heading) section.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "L"
}
```

