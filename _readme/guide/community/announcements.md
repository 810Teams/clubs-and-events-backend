## Announcements Tab

By visiting any community page, the announcements tab is the first tab to be shown, simply the default tab.

### List Announcements

`GET api/asset/announcement?community={int}`

The `{int}` is the ID of the community.

### Edit and Delete Announcement Button

After listing all announcements of the community, in each announcement object, there will be a field `is_able_to_edit`. If is `true`, render the edit and delete announcement buttons.

### Update Announcement

`PUT api/asset/announcement/{int}`

`PATCH api/asset/announcement/{int}`

```json
{
    "text": "string",
    "image": "image",
}
```

### Create Announcement Button

`GET api/commununity/club/{int}`

`GET api/commununity/event/{int}`

`GET api/commununity/event/community/{int}`

`GET api/commununity/lab/{int}`

After retrieving the community data by one of these API endpoints, a field `is_able_to_manage` is expected. If is `true`, then render the create announcement button, meaning the current user is able to create announcements in the certain community.

### Create Announcement

Make sure to pass the current community's ID automatically in to this request.

`POST api/asset/announcement`

```json
{
    "text": "string",
    "image": "image",
    "community": "int" // Must be auto
}
```

### Search Announcements

Announcements can be searched within a certain community, make sure to implement the search box for the announcements tab.

`GET api/asset/announcement?community={int}&search={string}`

The `{int}` is the ID of the community, which must be made auto, and `{string}` is the search query.
