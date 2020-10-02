# Design Guide - Community Page (Requests Tab)

## Requests Tab

Requests tab is the 5th tab next to the members tab, or being the 4rd if present in the event or the community event page.

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

Normal members can see all pending requests, but are not able to accept or decline them. Staff and members with a higher position can do this. Upon calling one of the APIs mentioned in the [Rendering the Tab][#rendering-the-tab] section, the field `is_able_to_manage` is expected. If is `true`, it means that the current logged-in member has permissions to manage the community, so render the accept and decline request buttons for them.

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
