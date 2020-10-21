# Design Guide - Notifications Bar

## List Notifications

Notifications bar is a bar containing all notifications the user received. Call this API to list all notifications the current user received.

`GET api/notification/notification`

No need to worry about the notification owner, the API will automatically filter out other users' notification. Users are not able to see other users' notifications in the first place.

## Clicking the Notification

There are 5 types of notifications, clicking them will redirect the user to the different pages. Look for the field `meta`, which will contains 3 sub-fields, including `notification_type`, `object_id`, and `community_id`.

Use the data from the fiend `community_id` to make redirections according to the following table.

Notification Type|Redirect
:-:|:-
request|Requests tab of the community page
membership_log|Community page
announcement|Announcements tab of the community page
community_event|Community event page
event|Event page

For displaying text, use `object_id` to retrieve the correct object, then display text according to the following table.

Notification Type|Use object ID to retrieve|Then use field|Then display
:-:|:-:|:-:|:-
request|Request|user, community|{user} has requested to join {community.name_en}.
membership_log|MembershipLog|log_text|{log_text}
announcement|Announcement|created_by, community|{created_by.name} has made an announcement in {community.name_en}
community_event|CommunityEvent|name_en, created_under, created_by|{created_by.name} has created a community event {name_en} in {created_under.name_en}
event|Event|name_en, created_by|{created_by.name} has started an event {name_en}
