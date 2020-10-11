# Design Guide - Notifications Bar

## List Notifications

Notifications bar is a bar containing all notifications the user received. Call this API to list all notifications the current user received.

`GET api/notification/notification`

No need to worry about the notification owner, the API will automatically filter out other users' notification. Users are not able to see other users' notifications in the first place.

## Clicking the Notification

There are 5 types of notifications, clicking them will redirect the user to the different pages. Look for the field `meta`, which will contains 2 sub-fields, including `notification_type` and `object_id`.

Notification Type|Redirect
:-:|:-
request|Requests tab of the community page
membership_log|Community page
announcement|Announcements tab of the community page
community_event|Community event page
event|Event page

After determining the notification type, use the object ID to redirect the user to the correct page.
