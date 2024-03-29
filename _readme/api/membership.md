# Membership Application API Endpoints

## Request

### List Requests

`GET api/membership/request`

- Token is required.
- Only shows requests that the current user is the requestor or to members of the community that is being requested to join.

#### URL Parameters

`user={int}`

`community={int}`

`status={string}`

### Retrieve Request

`GET api/membership/request/{int}`

- Token is required.
- Must be the requestor or to members of the community that is being requested to join.

### Create Request

`POST api/membership/request`

```json
{
    "community": "int"
}
```

- Token is required.
- If the community doesn't accept requests, a status code `400` will be returned.
- If the community is community event and doesn't allow outside participators, a status code `400` will be returned.
- If the requestor is already a member, a status code `400` will be returned.
- If the requestor already has a pending request, a status code `400` will be returned.
- If the requestor already has a pending invitation, a status code `400` will be returned.

### Update Request

`PUT api/membership/request/{int}`

`PATCH api/membership/request/{int}`

```json
{
    "status": "string (A, D)"
}
```

- Token is required.
- Must be the staff of the community.
- If the field `status` is updated to `'A'` (Accepted), a membership object will be automatically created.
- If the field `status` is updated to `'D'` (Declined), nothing happens.
- If the field `status` is updated to `'W'` (Waiting), a status code `400` will be returned.

### Delete Request

`GET api/membership/request/{int}`

- Token is required.
- Must be the requestor.
- This is equivalent to cancelling the request.

## Invitation

### List Invitations

`GET api/membership/invitation`

- Token is required.
- Only shows invitations that the current user is the invitee or the member of the community.

#### URL Parameters

`invitor={int}`

`invitee={int}`

`community={int}`

`status={string}`

### Retrieve Invitation

`GET api/membership/invitation/{int}`

- Token is required.
- Must the invitee or the member of the community.

### Create Invitation

`POST api/membership/invitation`

```json
{
    "community": "int",
    "invitee": "int"
}
```

- Token is required.
- If the community is community event and doesn't allow outside participators, a status code `400` will be returned.
- If the invitor is not a staff of the community, a status code `400` will be returned.
- If the invitee is already a member of the communtiy, a status code `400` will be returned.
- If the invitee already has a pending request, a status code `400` will be returned.
- If the invitee already has a pending invitation, a status code `400` will be returned.

### Update Invitation

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "string (A, D)"
}
```

- Token is required.
- Must be the invitee.
- If the field `status` is updated to `'A'` (Accepted), a membership object will be automatically created.
- If the field `status` is updated to `'D'` (Declined), nothing happens.
- If the field `status` is updated to `'W'` (Waiting), a status code `400` will be returned.

### Delete Invitation

`DELETE api/membership/invitation/{int}`

- Token is required.
- Must be the invitor.
- This is equivalent to cancelling the invitation.

## Membership

### List Memberships

`GET api/membership/membership`

- Token is optional.
- If a token is present, memberships in non-publicly visible communities will also be shown.

#### URL Parameters

`user={int}`

`community={int}`

`position={int}`

`status={string}`

`community_type={string:club|event|community_event|lab}`

### Retrieve Membership

`GET api/membership/membership/{int}`

- Token is optional.
- If a token is present, memberships in non-publicly visible communities will also be retrievable.

### Update Membership

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

- Token is required.
- If attempted to update both `position` and `status` fields at the same time, a status code `400` will be returned.

#### Position Assignation

```json
{
    "position": "int (0, 1, 2, 3)"
}
```

- Requires own membership position of 2 or 3.
- Not able to assign own position.
- If your membership position is 2, the field `position` must be 0 or 1, otherwise, a status code `400` will be returned.
- If your membership position is 3, the field `position` can be anything from 0 to 3, but if 3 is input, your position will be demoted to 2.

#### Retirement and Leaving

```json
{
    "status": "string (R, L)"
}
```

- Requires own membership position of 0, 1, or 2.
- If attemped to memberships that are not your own, a status code `400` will be returned.

#### Member Removal

```json
{
    "status": "X"
}
```

- Requires own membership position of 2 or 3.
- The position of the member that is going to be removed must be lower than own position.
- If attempted on own membership, a status code `400` will be returned.

## Default Membership Label

### Retrieve Default Membership Labels

`GET api/membership/membership/label/default`

## Custom Membership Label

### List Custom Membership Labels

`GET api/membership/membership/label/custom`

- Token is optional.
- If a token is present, custom membership labels of memberships in non-publicly visible communities will also be shown.

### Retrieve Custom Membership Label

`GET api/membership/membership/label/custom/{int}`

- Token is optional.
- If a token is present, custom membership labels of memberships in non-publicly visible communities will also be retrievable.

### Create Custom Membership Label

`POST api/membership/membership/label/custom`

```json
{
    "label": "string",
    "membership": "int"
}
```

- Token is required.
- If own position is not 2 or 3, a status code `400` will be returned.
- If the targeted membership position is not 1 or 2, a status code `400` will be returned.

### Update Custom Membership Label

`PUT api/membership/membership/label/custom/{int}`

`PATCH api/membership/membership/label/custom/{int}`

```json
{
    "label": "string",
}
```

- Token is required.
- Own position must be 2 or 3.
- Targeted membership position must be 1 or 2.

### Delete Custom Membership Label

`DELETE api/membership/membership/label/custom/{int}`

- Token is required.
- Own position must be 2 or 3.

## Membership Log

### List Membership Logs

`GET api/membership/membership/log`

- Token is optional.
- If a token is present, membership logs of memberships in non-publicly visible communities will also be shown.

#### URL Parameters

`user={int}`

`community={int}`

`exclude_current_memberships={boolean}`

`position={int}`

`status={string:A|R|L|X}`

### Retrieve Membership Log

`GET api/membership/membership/log/{int}`

- Token is optional.
- If a token is present, membership logs of memberships in non-publicly visible communities will also be retrievable.

### Retrieve Past Memberships

`GET api/membership/membership/past/{int}`

- Token is optional.
- If a token is present, entries of memberships in non-publicly visible communities will also be retrievable.
- `{int}` is the ID of the user.

## Advisory

### List Advisories

`GET api/membership/advisory`

- Token is required.

### Retrieve Advisory

`GET api/membership/advisory/{int}`

- Token is required.

### Create Advisory

`POST api/membership/advisory`

```json
{
    "advisor": "int",
    "community": "int",
    "start_date": "date",
    "end_date": "date"
}
```

- Token is required.
- Must be an active student committee member.
- If attempted to make non-lecturer an advisor, a status code `400` will be returned.
- If attempted to make an overlapped advisory, a status code `400` will be returned.
- If attempted to make a start date come before an end date, a status code `400` will be returned.

## Approval Request

### List Approval Requests

`GET api/membership/approval-request`

- Token is required.
- Must be either a leader of the community to see a certain approval request, or be a student committee member to see every approval request.

#### URL Parameters

`community={int}`

`status={int}`

### Retrieve Approval Request

`GET api/membership/approval-request/{int}`

- Token is required.
- Must be either a leader of the community to see a certain approval request, or be a student committee member to see every approval request.

### Create Approval Request

`POST api/membership/approval-request`

```json
{
    "community": "int",
    "message": "string",
    "attached_file": "file"
}
```

- Token is required.
- If attempted to create an approval request from the lab or community event, a status code `400` will be returned.
- If attempted to create an approval request from the club or event you are not a leader, a status code `400` will be returned.

### Update Approval Request

`PUT api/membership/approval-request/{int}`

`PATCH api/membership/approval-request/{int}`

```json
{
    "status": "string (A, D)"
}
```

- Token is required.
- Must be a student committee member.
- If attempted to update the status to `'W'`, a status code `400` will be returned.

### Delete Approval Request

`DELETE api/membership/approval-request/{int}`

- Token is required.
- Must be a leader of the community.
