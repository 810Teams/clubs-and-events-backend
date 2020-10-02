# Design Guide - Index

## Club Tab

The club tab is where all clubs reside. A separator between official clubs and unofficial clubs is required if the user is authenticated and at least one unofficial club is received from the API.

If the user is not authenticated, any unofficial clubs and non-publicly visible clubs will be automatically filtered out by the API.

### List Official Clubs

`GET api/community/club?is_official=1`

### List Unofficial Clubs

`GET api/community/club?is_official=0`

### Create Club Button

In the club tab, a create club button should appear for the student users. First, call this API to retrieve the current user.

`GET api/user/user/me`

The field `is_lecturer` is expected, if is `false`, it means that the user is student. Meaning, the user can create clubs, so render the create club button.

### Create Clubs

After the user clicked the create club button, redirect the user to the club creation page, with the form. After the user has filled all the required information and confirmed the club creation, call this API to create the club.

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

## Event Tab

The event tab is where all events reside. No separator is needed, but an API is needed to be called twice.

If the user is not authenticated, any unapproved events and non-publicly visible events will be automatically filtered out by the API.

### List Events

`GET api/community/event`

### List Community Events

`GET api/community/event/community`

### Create Events

Events can be created by both students and lecturers, so render the button if the user is authenticated. After the user clicked the create event button, redirect the user to the event creation page, with the form. After the user has filled all the required information and confirmed the event creation, call this API to create the event.

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

## Lab Tab

The lab tab is where all labs reside. Just call an API and everything is done.

If the user is not authenticated, any non-publicly visible labs will be automatically filtered out by the API.

### List Labs

`GET api/community/lab`

### Create Lab Button

In the lab tab, a create lab button should appear for the users. First, call this API to retrieve the current user.

`GET api/user/user/me`

The field `is_lecturer` is expected, if is `false`, it means that the user is student. Meaning, the user can create clubs, so render the create lab button.

### Create Labs

After the user clicked the create lab button, redirect the user to the lab creation page, with the form. After the user has filled all the required information and confirmed the lab creation, call this API to create the club.

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

## Search Bar

The search bar can be used to search for clubs, events, and labs. API is needed to be called 4 times as listed here below.

`GET api/community/club?search={string}`

`GET api/community/event?search={string}`

`GET api/community/event/community?search={string}`

`GET api/community/lab?search={string}`

The `{string}` is the search query.

## Profile Icon

The profile icon reside at the top right of the screen, which links to your own profile. The current user can be retrieve with this API endpoint. Please note that this API endpoint does not accept any other requests than the `GET` request.

`GET api/user/user/me`
