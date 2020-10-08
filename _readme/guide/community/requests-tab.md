# Design Guide - Community Page (Requests Tab)

## Requests Tab

Requests tab is the 5th tab next to the members tab. This tab displays all the pending requests to the community and all invitations made by members.

### Rendering the Tab

This tab is invisible and must be unaccessable to non-members. Depends on the community type, call this API to see if the current logged-in user is the member or not.

`GET api/community/club/{int}`

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

`GET api/community/lab/{int}`

The field `own_membership` is expected. If is not `null`, then render the tab.

### List Requests

Render all pending requests received by calling this API.

`GET api/membership/request?community={int}&status=W`

### Render the Accept and Decline Request Buttons

Normal members can see all pending requests, but are not able to accept or decline them. Staff and members with a higher position can do this. Upon calling one of the APIs mentioned in the [Rendering the Tab][#rendering-the-tab] section, the field `own_membership_position` is expected. If is at least `1`, it means that the current logged-in member has permissions to manage the community, so render the accept and decline request buttons for them.

### Accepting the Request

Accepting the request is equivalent to updating the request, which can be done by calling one of these two APIs, with the exact value as described in the JSON below.

`PUT api/membership/request/{int}`

`PATCH api/membership/request/{int}`

```json
{
    "status": "A"
}
```

No need to worry about the membership, which will be automatically created upon the request is accepted.

### Declining the Request

Declining the request is equivalent to updating the request, which can be done by calling one of these two APIs, with the exact value as described in the JSON below.

`PUT api/membership/request/{int}`

`PATCH api/membership/request/{int}`

```json
{
    "status": "D"
}
```

No need to worry about the membership, which will be automatically created upon the request is accepted.

### List Invitations

After rendering all the requests, place a separator, then render all the outgoing pending invitations. Use this API to retrieve all invitations related to the community.

`GET api/membership/invitation?community={id}&status=W`

### Render Cancel Invitation Button

Being the invitor means you can cancel the invitations you made, but that is not it. Invitations you made can also be cancelled by other members in the community with a position of 2 or 3.

To render the cancel button, look for the field `is_able_to_cancel` from calling the API above in the [list invitations](#list-invitations) section. If is `true`, then render the cancel button.

### Cancel Invitation

Cancelling the invitation is equivalent to deleting the invitation itself. Call this API to cancel the invitation.

`DELETE api/membership/invitation/{id}`
