# Design Guide - Profile

## Profile Page

Depends where this page is accessed from, if this page is accessed from the top-right profile button, then it is supposed to be your own profile.

However, wherever this page is accessed from, the specific ID of the user is recommended to be used in the URL, instead of using the flexible current user API endpoint.

### Retrieve User

`GET api/user/user/{int}`

### Rendering Edit Profile Button

After retrieving the user, call this API to retrieve the current logged-in user and check if the ID matches. If matches, render the edit profile button.

`GET api/user/user/me`

### Update User

After clicking the edit profile button, the user will be redirected to the edit profile page, displaying the form for the user. There is a few fields, but only 6 of these fields below can be edited.

`PUT api/user/user/{int}`

`PATCH api/user/user/{int}`

```json
{
    "email": "string",
    "nickname": "string",
    "bio": "string",
    "profile_picture": "image",
    "cover_photo": "image",
    "birthdate": "date",
}
```
