## Edit Page

The edit page is the page where the user can edit the community. Depending on the type of the community, API endpoints will be different.

This page can be access from the button in the header of the community page, read the [header guide](header.md#get-available-actions) for the guide in rendering the buttons.

### Update Club

`PUT api/community/club/{int}`

`PATCH api/community/club/{int}`

```json
{
    "name_th": "string",
    "name_en": "string",
    "description": "string",
    "external_links": "string",
    "logo": "image",
    "banner": "image",
    "is_accepting_requests": "boolean",
    "founded_date": "date",
    "status": "string (R, C, D)",
    "club_type": "int"
}
```

### Delete Club

`DELETE api/community/club/{int}`

### Update Event

`PUT api/community/event/{int}`

`PATCH api/community/event/{int}`

```json
{
    "name_th": "string",
    "name_en": "string",
    "description": "string",
    "external_links": "string",
    "logo": "image",
    "banner": "image",
    "is_accepting_requests": "boolean",
    "location": "string",
    "start_date": "date",
    "end_date": "date",
    "start_time": "time",
    "end_time": "time",
    "is_cancelled": "boolean",
    "event_type": "int",
    "event_series": "int"
}
```

#### Approved Event

In case of approved events, 2 additional fields can be used in `PUT` and `PATCH` requests.

```json
{
    "url_id": "string",
    "is_publicly_visible": "boolean",
}
```

### Delete Event

`DELETE api/community/event/{int}`

### Update Community Event

`PUT api/community/event/community/{int}`

`PATCH api/community/event/community/{int}`

```json
{
    "name_th": "string",
    "name_en": "string",
    "description": "string",
    "external_links": "string",
    "logo": "image",
    "banner": "image",
    "is_accepting_requests": "boolean",
    "location": "string",
    "start_date": "date",
    "end_date": "date",
    "start_time": "time",
    "end_time": "time",
    "is_cancelled": "boolean",
    "allows_outside_participator": "boolean",
    "event_type": "int",
    "event_series": "int",
}
```

### Delete Community Event

`DELETE api/community/event/community/{int}`

### Update Lab

`PUT api/community/lab/{int}`

`PATCH api/community/lab/{int}`

```json
{
    "name_th": "string",
    "name_en": "string",
    "url_id": "string",
    "description": "string",
    "external_links": "string",
    "logo": "image",
    "banner": "image",
    "is_accepting_requests": "boolean",
    "room": "string",
    "founded_date": "date",
    "tags": "string",
    "status": "string (R, C, D)",
}
```

### Delete Lab

`DELETE api/community/lab/{int}`
