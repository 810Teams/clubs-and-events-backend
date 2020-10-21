# Asset Application API Endpoints

## Announcement

### List Announcements

`GET api/asset/announcement`

- Token is optional.
- If a token is present, announcements in non-publicly visible communities will also be shown.

#### URL Parameters

`search={string}` to search for text.

`community={int}`

`is_publicly_visible={boolean}`

### Retrieve Announcement

`GET api/asset/announcement/{int}`

- Token is optional.
- If a token is present, announcements in non-publicly visible communities will also be retrievable.

### Create Announcement

`POST api/asset/announcement`

```json
{
    "text": "string",
    "image": "image",
    "is_publicly_visible": "boolean",
    "community": "int"
}
```

- Token is required.
- Must a member of the community creating in as described in the field `community` with a position of 1, 2, or 3, otherwise, a status code `400` will be returned.

### Update Announcement

`PUT api/asset/announcement/{int}`

`PATCH api/asset/announcement/{int}`

```json
{
    "text": "string",
    "image": "image",
    "is_publicly_visible": "boolean"
}
```

- Token is required.
- Must a member of the community creating in with a position of 1, 2, or 3.

### Delete Announcement

`DELETE api/asset/announcement/{int}`

- Token is required.
- Must a member of the community creating in with a position of 1, 2, or 3.

## Album

### List Albums

`GET api/asset/album`

- Token is optional.
- If a token is present, albums in non-publicly visible communities will also be shown.

#### URL Parameters

`search={string}` to search for album name.

`community={int}`

### Retrieve Album

`GET api/asset/album/{int}`

- Token is optional.
- If a token is present, albums in non-publicly visible communities will also be retrievable.

### Create Album

`POST api/asset/album`

```json
{
    "name": "string",
    "community": "int",
    "community_event": "int"
}
```

- Token is required.
- Must a member of the community this album creating in as described in the field `community` with a position of 1, 2, or 3, otherwise, a status code `400` will be returned.
- If attempted to create under a community event, a status code `400` will be returned.
- If community is event, but attempted to link the album to community events, a status code `400` will be returned.
- If attempted to link the album to community events created under other communities as described in the field `community`, a status code `400` will be returned.

### Update Album

`PUT api/asset/album/{int}`

`PATCH api/asset/album/{int}`

```json
{
    "name": "string",
    "community_event": "int"
}
```

- Token is required.
- Must a member of the community this album creating in with a position of 1, 2, or 3.
- If community is event, but attempted to link the album to community events, a status code `400` will be returned.
- If attempted to link the album to community events created under other communities as described in the field `community`, a status code `400` will be returned.

### Delete Album

`DELETE api/asset/album/{int}`

- Token is required.
- Must a member of the community this album creating in with a position of 1, 2, or 3.

## Album Image

### List Album Images

`GET api/asset/album`

- Token is optional.
- If a token is present, album images of albums in non-publicly visible communities will also be shown.

#### URL Parameters

`album={int}`

`limit={int}`

### Retrieve Album Image

`GET api/asset/album/{int}`

- Token is optional.
- If a token is present, album images of albums in non-publicly visible communities will also be retrievable.

### Create Album Image

`POST api/asset/album`

```json
{
    "image": "image",
    "album": "int"
}
```

- Token is required.
- Must a member of the community the targeted album is created in with a position of 1, 2, or 3, otherwise, a status code `400` will be returned.

### Delete Album Image

`DELETE api/asset/album/{int}`

- Token is required.
- Must a member of the community the targeted album is created in with a position of 1, 2, or 3, otherwise, a status code `400` will be returned.

## Comment

### List Comments

`GET api/asset/comment`

#### URL Arguments

`search={string}` to search for text and the writer.

`event={int}`

### Retrieve Comment

`GET api/asset/comment/{int}`

### Create Comment

`POST api/asset/comment`

```json
{
    "text": "string",
    "written_by": "string",
    "event": "int"
}
```
