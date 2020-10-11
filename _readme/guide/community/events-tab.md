# Design Guide - Community Page (Events Tab)

## Events Tab

The events tab is the 3rd tab next to the albums tab. This tab only exists in the club and lab pages, meaning this tab is where all community events of the certain club or lab reside.

### List Community Events

`GET api/community/event/community?created_under={int}`

The `{int}` is the ID of the community, used to filter only community events created under here.

### Create Community Event Button

`GET api/commununity/club/{int}`

`GET api/commununity/event/{int}`

`GET api/commununity/event/community/{int}`

`GET api/commununity/lab/{int}`

After retrieving the community data by one of these APIs, a field `own_membership_position` is expected. If is at least `1`, then render the create community event button, meaning the current user is able to create community events in the certain community.

### Create Community Event

After the user has clicked the create community event button, display the form. Within the form, call these two API to retrieve the event types and event series as the choices for the user to pick.

`GET api/category/event-type`

`GET api/category/event-series`

After the user has filled all the required information and confirmed the community event creation, call this API to create the community event.

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
