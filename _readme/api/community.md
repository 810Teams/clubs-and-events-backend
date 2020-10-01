# Community Application API Endpoints

## Club

### List Clubs

`GET api/community/club`

- Token is optional.
- If a token is present, non-publicly visible clubs will also be shown.

#### URL Parameters

`search={string}` to search for Thai name, English name, and description.

`club_type={int}`

`is_official={boolean}`

`status={string}`

### Retrieve Club

`GET api/community/club/{int}`

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

`DELETE api/community/club/{int}`

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

`search={string}` to search for Thai name, English name, description, and location.

`event_type={int}`

`event_series={int}`

`is_approved={boolean}`

`is_cancelled={boolean}`

### Retrieve Event

`GET api/community/event/{int}`

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

- Token is required.
- Must be a student.
- Must have a membership with a position of 2 or 3.

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

- Token is required.
- Must be a student.
- Must have a membership with a position of 3.
- Must not be an approved event.

## Community Event

### List Community Events

`GET api/community/event/community`

- Token is optional.
- If a token is present, non-publicly visible events will also be shown.

#### URL Parameters

`search={string}` to search for Thai name, English name, description, and location.

`event_type={int}`

`event_series={int}`

`is_approved={boolean}`

`is_cancelled={boolean}`

`created_under={int}`

`allows_outside_participators={boolean}`

### Retrieve Community Event

`GET api/community/event/community/{int}`

- Token is optional.
- If a token is present, non-publicly visible events will also be retrievable.

### Create Community Event

`POST api/community/event/community`

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
    "created_under": "int"
}
```

- Token is required.
- Must be a member with a position of 1, 2, or 3 in the community created under as described in the field `created_under`, otherwise, a status code of `400` will be returned.
- If attempted to create under other events, a status code of `400` will be returned.

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

- Token is required.
- Must be a member with a position of 2 or 3 in the community created under as described in the field `created_under`, or a member with a position of 2 or 3 of the community event.

### Delete Community Event

`DELETE api/community/event/community/{int}`

- Token is required.
- Must be a member with a position of 3 in the community created under as described in the field `created_under`, or a member with a position of 3 of the community event.

## Lab

### List Labs

`GET api/community/lab`

- Token is optional.
- If a token is present, non-publicly visible labs will also be shown.

#### URL Parameters

`search={string}` to search for Thai name, English name, description, and tags.

`status={string}`

### Retrieve Lab

`GET api/community/lab/{int}`

- Token is optional.
- If a token is present, non-publicly visible labs will also be retrievable.

### Create Lab

`POST api/community/lab`

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

- Token is required.
- Must be a lecturer.

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

- Token is required.
- Must be a lecturer.
- Must have a membership with a position of 2 or 3.

### Delete Lab

`DELETE api/community/lab/{int}`

- Token is required.
- Must be a lecturer.
- Must have a membership with a position of 3.
