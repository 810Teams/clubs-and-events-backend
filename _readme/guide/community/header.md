## Heading

By visiting any community page, simply it means that the client must call one of these 4 API endpoints to retrieve the community's data. Make sure to display all important information.

`GET api/community/club/{int}`

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

`GET api/community/lab/{int}`

### Rendering the Request Button

Request button simply means request to join button. This requires an API testing, since duplicating the multiple cases is not the best practice. Let's say that the button should always be rendered first, then take a look at these cases to see if the button should be disabled or modified.

#### Case 1 - Already a member

Check if the user is already an active or retired member by verifying the data from calling one of the API endpoints above in the [heading](#heading) section. If the field `own_membership_id` is not `null`, no need to render the request button.

#### Case 2 - Community is not accepting requests

Check if the community accepts requests by verifying the data from calling one of the API endpoints above in the [heading](#heading) section. If the field `is_accepting_requests` is `false`, then disable the request button, with notes.

#### Case 3 - Community event does not allow outside participators

Check if the community is community event and allows outside participators or not by verifying the data from calling one of the API endpoints above in the [heading](#heading) section. If the field `allows_outside_participators` presents, meaning that the object is the community event, and if the value is `false`, then disable the request button, with notes.

#### Case 4 - Pending request exists

If this does not return an empty list, meaning the user is not able to request due to already having a pending request. In this case, render the [cancel request](#cancelling-request) button instead.

`GET api/membership/request?user={int}&community={int}&status=W`

The first `{int}` is the ID of the current user and the second `{int}` is the ID of the community.

#### Case 5 - Pending invitation exists

If this does not return an empty list, meaning the user is not able to request due to already having a pending invitation. In this case, render the [accept and decline invitation](#accept-or-decline-invitation) buttons instead.

`GET api/membership/invitation?invitee={int}&community={int}&status=W`

The first `{int}` is the ID of the current user and the second `{int}` is the ID of the community.

### Requesting to Join

By clicking the request button, this API endpoint must be called.

`POST api/membership/request`

```json
{
    "community": "int"
}
```

The `"int"` is the ID of the community user requested to join, must be auto.

### Cancelling Request

If the user clicked the cancel request button, use this API endpoint. Deleting a pending join request is equivalent to cancelling the join request.

`DELETE api/membership/request/{int}`

The `{int}` is the ID of the request, can be obtained by calling this API endpoint, and retrieve the ID of the first object in the list. The length of the list should never exceed 1 from begin.

`GET api/membership/request?user={int}&community={int}&status=W`

### Accept or Decline Invitation

If the user clicked the accept invitation button, use one of these two API endpoints.

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "A"
}
```

If the user clicked the decline invitation button, use one of these two API endpoints.

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "D"
}
```

### Get Available Actions

Upon calling one of the API endpoints above in the [heading](#heading) section, a field `available_actions` is expected, then check if the list contains these values.

|Code|Action|
|:-:|:-|
|"E"|Renders a button that let the current user edit the community.|
|"D"|Renders a button that let the current user delete the community separately in the [edit page](edit-page.md).|
|"A"|Renders a button that revert user from being retired to active.|
|"R"|Renders a button that set the current user's membership status to retired.|
|"L"|Renders a button that let the current user leaves the community.|

These are actions, all should be placed in the same pop-up menu button, unlike request button which is an individual button. This is to prevent accidental action performings.

For the action code `E` and `D`, render the edit community button, and visit the [edit page](edit-page.md) for the further guide.

### Retiring from Community

The membership ID can be retrieved from the community object from calling one of the API endpoints as described in the [heading](#heading) section.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "R"
}
```

### Back in Duty to Community

The membership ID can be retrieved from the community object from calling one of the API endpoints as described in the [heading](#heading) section.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "A"
}
```

### Leaving Community

The membership ID can be retrieved from the community object from calling one of the API endpoints as described in the [heading](#heading) section.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "L"
}
```

