# Design Guide - Community Page (Albums Tab)

## Albums Tab

The albums tab is the 2nd tab next to the announcement tab. This tab works differently in the community events, so read carefully.

### List Albums

After the user accessed the album tab, all albums of the community will be shown.

`GET api/asset/album?community={int}`

The `{int}` is the ID of the community.

For community events, use this API instead, which will list all albums linked to it.

`GET api/asset/album?community_event={int}`

### List Album Images for Album Preview

Listing the albums requires some images to be displayed as a preview of the album.

`GET api/asset/album/image?album={int}&limit={int}`

The first `{int}` is the ID of the album, must be made auto, then the next `{int}` determines how many images should be loaded at maximum. This is to prevent excessive data usage and server loads, recommended at 1 to 4.

### Retrieve Album and its Images

Clicking into the album, the album detail and all images of the album should be loaded. First, use this API to load the album details.

`GET api/asset/album/{int}`

The `{int}` is the ID of the album. Then, load all album images using this API.

`GET api/asset/album/image?album={int}`

The `{int}` is the ID of the album, must be made auto.

### Edit Album, Upload Images, and Delete Album Buttons

Upon retrieving album, the field `is_able_to_edit` is expected. If is `true`, then render the edit album button. After clicking that button, it will switch to the album edit mode, which the upload images button and the delete button will also appear.

### Update Album and Images

In the album edit mode, you can edit album details, add images, and delete images.

Starting with updating the album itself.

`PUT api/asset/album/{int}`

`PATCH api/asset/album/{int}`

```json
{
    "name": "string",
    "community_event": "int"
}
```

For any new images added, a `POST` request of album image must be called.

`POST api/asset/album/image`

```json
{
    "image": "image",
    "album": "int"
}
```

For any images deleted, a `DELETE` request of album image must be called.

`DELETE api/asset/album/image/{int}`

To summarize, users can only add or delete images in the album, no updating.

### Delete Album

Albums can be edited along with updating the album and deleting images. Call this API to delete the album. No need to worry about the images since they will be deleted along with the album automatically.

`DELETE api/asset/album/{int}`

### Create Album Button

`GET api/community/club/{int}`

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

`GET api/community/lab/{int}`

After retrieving the community data by one of these APIs, a field `own_membership_position` is expected. If is at least `1`, then render the create album button, meaning the current user is able to create albums in the certain community.

### Create Album

Make sure to pass the current community's ID automatically in to this request.

`POST api/asset/album`

```json
{
    "name": "string",
    "community": "int",
    "community_event": "int"
}
```

If the album is going to be created in the event, the field `community_event` must be `null` automatically, otherwise, a status code of `400` will be returned.

If the album is going to be created in the community event, the field `community` must be set to its parent community automatically, otherwise, a status code of `400` will be returned. The community event will be put into the field `community_event` instead, meaning, the album is actually created in the club or the lab, and linked to the community event.

### Community Event Linking Choices

Creating and updating album give users an option to link the album to any community events created under the designated community. It is the best practice to make the field `community_event` a dropdown choice, and here is how to filter those choices.

`GET api/community/event/community?created_under={int}`

The `{int}` is the ID of the community that the album is created in, must be made auto.
