# Community Application API Endpoints

## Club

### List Clubs

`GET api/community/club`

- Token is optional.
- If a token is present, non-publicly visible clubs will also be shown.

#### URL Parameters

`club_type={int}`

`is_official={boolean}`

`status={character}`

### Retrieve Club

`GET api/community/club/{id}`

- Token is optional.
- If a token is present, non-publicly visible clubs will also be retrievable.

### Create Club

`POST api/community/club`

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

- Token is required.
- Must be a student.

### Update Club

`PUT api/community/club/{id}`

`PATCH api/community/club/{id}`

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

- Token is required.
- Must be a student.
- Must have a membership with a position of 2 or 3.

#### Official Club

In case of official clubs, 3 additional fields can be used in `PUT` and `PATCH` requests.

```json
{
    "url_id": "string",
    "is_publicly_visible": "boolean",
    "room": "string"
}
```

### Delete Club

`DELETE api/community/club/{id}`

- Token is required.
- Must be a student.
- Must have a membership with a position of 3.
- Must not be an official club.

## Event

### List Events

`GET api/community/event`

- Token is optional.
- If a token is present, non-publicly visible events will also be shown.

#### URL Parameters

`event_type={int}`

`event_series={int}`

`is_approved={boolean}`

`is_cancelled={boolean}`

### Retrieve Event

`GET api/community/event/{id}`

- Token is optional.
- If a token is present, non-publicly visible events will also be retrievable.

### Create Event

`POST api/community/event`

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

- Token is required.
- Must be a student.

### Update Event

`PUT api/community/event/{id}`

`PATCH api/community/event/{id}`

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

- Token is required.
- Must be a student.
- Must have a membership with a position of 2 or 3.

#### Official Event

In case of approved events, 2 additional fields can be used in `PUT` and `PATCH` requests.

```json
{
    "url_id": "string",
    "is_publicly_visible": "boolean",
}
```

### Delete Event

`DELETE api/community/event/{id}`

- Token is required.
- Must be a student.
- Must have a membership with a position of 3.
- Must not be an approved event.
