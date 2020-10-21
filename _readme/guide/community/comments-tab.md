# Design Guide - Community Page (Comments Tab)

## Comments Tab

The events tab is the 3rd tab next to the albums tab. This tab only exists in the event and community event pages, simply replacing the events tab in the club and lab pages.

### List Comments

`GET api/asset/comment?event={int}`

The `{int}` is the ID of the event.

### Render Create Comment Button

`GET api/commununity/club/{int}`

`GET api/commununity/event/{int}`

`GET api/commununity/event/community/{int}`

`GET api/commununity/lab/{int}`

After retrieving the community data by one of these APIs, a field `available_actions` is expected. If `"comment"` is in the list, then render the create comment button, meaning the current user or the current session allows creating comments in the event. See all available actions [here](header.md/###get-available-actions).

### Create Comment

Anyone can create comments, even without authorization, so render the button.

`POST api/asset/comment`

```json
{
    "text": "string",
    "written_by": "string",
    "event": "int"
}
```

The field `event` must be auto.

### Search Comments

The comments can be searched by text and the writer's name. Render the search box, and call this API to search for comments.

`GET api/asset/comment?event={int}&search={string}`

The `{string}` is the search query.
