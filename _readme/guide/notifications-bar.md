# Design Guide - Notifications Bar

## List Notifications

Notifications bar is a bar containing all notifications the user received. Call this API to list all notifications the current user received.

`GET api/notification/notification`

No need to worry about the notification owner, the API will automatically filter out other users' notification. Users are not able to see other users' notifications in the first place.

## Clicking the Notification

There are 5 types of notifications, clicking them will redirect the user to the different pages. Look for the field `meta`, which will contains 4 sub-fields, including `notification_type`, `object_id`, `community_id`, and `text`.

Take a look at the field `notification_type` to determine where the user should be redirected to, then use `community_id` to make redirections according to the following table.

Notification Type|Redirect
:-:|:-
request|Requests tab of the community page
membership_log|Community page
announcement|Announcements tab of the community page
community_event|Community event page
event|Event page

For displaying text, use the field `text` to retrieve the text, which can be used to display it instantly.

## Reading Notifications

Each notification object has a field `is_read` which determines that the user has already read this notification or not.

Upon user reads the notification, or clicking "Mark As Read" or "Mark All As Read", call on of these two APIs to update the notification object.

`PUT api/notification/notification/{int}`

`PATCH api/notification/notification/{int}`

```json
{
    "is_read": true
}
```

Design this system like Facebook's read status marking.

## Deleting Notifications

Having several notifications can be messy, so users can easily delete their notifications. Call this API to delete the notification.

`DELETE api/notification/notification/{int}`

Design this system like Facebook's delete notification system.