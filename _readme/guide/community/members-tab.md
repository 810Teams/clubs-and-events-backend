# Design Guide - Community Page (Members Tab)

## Members Tab

Members tab is the 4th tab next to the events tab. This tab displays all members of the community.

### List Memberships

Listing all members in the community requires 2 APIs, since there are 4 membership statuses, including `A` (active), `R` (retired), `L` (left), and `X` (removed), which `A` and `R` are still considered being a member of the community.

`GET api/membership/membership?community={id}&status=A`

`GET api/membership/membership?community={id}&status=R`

The `{id}` is the ID of the community.

After calling these 2 APIs, don't mix them, but sort each of them by position in the descending order. The member list page should be having a separator separating active members and retired members if at least 1 retired member is present.

### Rendering Assign Position Buttons

By being a position number of `2` or `3`, user can update other members' position. Upon calling the APIs above in the [list memberships](#list-memberships) section, a field `is_able_to_assign` is expected. This field contains a list of all assignable positions, so render buttons as the list said.

For example, this means the current user can demote this member to the normal member, promote to the deputy leader, or transfer own leader position to this member.

```json
{
    "is_able_to_assign": [
        0,
        2,
        3
    ]
}
```

#### Membership Position Names

||0|1|2|3|
:-:|:-:|:-:|:-:|:-:
Club|Member|Staff|Vice President|President
Event|Participator|Staff|Vice President|President
Community Event|Participator|Staff|Event Co-Creator|Event Creator
Lab|Lab Member|Lab Helper|Lab Co-Supervisor|Lab Supervisor

### Position Assignation

Positions can be assigned to a membership by calling one of these two APIs, with an only field of `position` as described below.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "position": "int (0, 1, 2, 3)"
}
```

### Rendering Remove Member Button

By being a position number of `2` or `3`, user can remove other members from the community. Technically by setting the membership status to `X`. Upon calling the APIs above in the [list memberships](#list-memberships) section, a field `is_able_to_remove` is expected. This field contains a boolean, being `true` means that this member can be removed from the community.

For example, this means the current user can remove this member from the community.

```json
{
    "is_able_to_remove": true
}
```

### Member Removal

Members can be removed from the community by calling one of these two APIs, with an only field `status` as described below, the data of this field must also be a string of `X` for it to work.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "X"
}
```

### Render Invite Button

Depends on the community type, call this API to see if the current logged-in user has permissions to manage the community or not.

`GET api/community/club/{int}`

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

`GET api/community/lab/{int}`

The field `is_able_to_manage` is expected. If is `true`, it means that the current logged-in member has permissions to manage the community, so render the invite button.

### Invite

The invite panel is the popup, like Facebook, the person doing the invitation can click which user to send the invitation.

Before that, a list of applicable users is required, so that errors will not occur. Call this API to list all users that are applciable for the community.

`GET api/user/user?is_applicable_for={int}`

The `{int}` is the ID of the community.

### Searching for Users

In the invite panel, the person doing the invitation can search for users to invite. Add the `search={string}` parameter to the API URL.

`GET api/user/user?is_applicable_for={int}&search={string}`

The `{string}` is the search query, can be used to search for the username, name, and nickname of users.
