## Members Tab

Members tab is the 4th tab next to the events tab, or being the 3rd if present in the event or the community event page.

### List Memberships

Listing all members in the community requires 2 API endpoints, since there are 4 membership statuses, including `A` (active), `R` (retired), `L` (left), and `X` (removed), which `A` and `R` are still considered being a member of the community.

`GET api/membership/membership?community={id}&status=A`

`GET api/membership/membership?community={id}&status=R`

The `{id}` is the ID of the community.

After calling these 2 API endpoints, don't mix them, but sort each of them by position in the descending order. The member list page should be having a separator separating active members and retired members if at least 1 retired member is present.

### Rendering Assign Position Buttons

By being a position number of `2` or `3`, user can update other members' position. Upon calling the API endpoints above in the [list memberships](#list-memberships) section, a field `is_able_to_assign` is expected. This field contains a list of all assignable positions, so render buttons as the list said.

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

||0|1|2|3
:-:|:-:|:-:|:-:|:-:
Club|Member|Staff|Vice President|President
Event|Participator|Staff|Vice President|President
Community Event|Participator|Staff|Event Co-Creator|Event Creator
Lab|Lab Member|Lab Helper|Lab Co-Supervisor|Lab Supervisor

### Position Assignation

Positions can be assigned to a membership by calling one of these two API endpoints, with an only field of `position` as described below.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "position": "int (0, 1, 2, 3)"
}
```

### Rendering Remove Member Button

By being a position number of `2` or `3`, user can remove other members from the community. Technically by setting the membership status to `X`. Upon calling the API endpoints above in the [list memberships](#list-memberships) section, a field `is_able_to_remove` is expected. This field contains a boolean, being `true` means that this member can be removed from the community.

For example, this means the current user can remove this member from the community.

```json
{
    "is_able_to_remove": true
}
```

### Member Removal

Members can be removed from the community by calling one of these two API endpoints, with an only field `status` as described below, the data of this field must also be a string of `X` for it to work.

`PUT api/membership/membership/{int}`

`PATCH api/membership/membership/{int}`

```json
{
    "status": "X"
}
```