# Design Guide - Invitations Bar

## List Invitations

Invitations bar is a bar containing all invitations the user received. Call this API to list all invitations the current user received.

`GET api/membership/invitation?invitee={int}`

The `{int}` is the ID of the current logged-in user.

## Accepting Invitations

Regardless of the invitation status, display all of them in the invitation bar in the different way in the descending order of the field `created_at`, the field `id` can also be used here. For the invitations with the status of `W` (waiting), display both accept and decline invitation buttons for the user.

After the user clicked accept invitation button, call this API, with the exact value as the JSON below.

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "A"
}
```

No need to worry about the membership, which will be automatically created upon the invitation is accepted.

## Declining Invitations

On the other hand, if the user clicked the decline invitation button, call this API instead, with the exact value as the JSON below.

`PUT api/membership/invitation/{int}`

`PATCH api/membership/invitation/{int}`

```json
{
    "status": "D"
}
```
