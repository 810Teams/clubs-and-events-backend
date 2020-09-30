# User Application API Endpoints

## Login

Use `POST api/user/login` to request a token.

```json
{
    "username": "string",
    "password": "string"
}
```

## User

### List All Users

Use `GET api/user/user` to list all users. **Token is optional.**

#### URL Parameters

Add `search={string}` to search for username, name, or nickname.

Add `is_active={boolean}` to filter for active users. **Token is required.**

Add `is_staff={boolean}` to filter for staff. **Token is required.**

Add `is_superuser={boolean}` to filter for superusers. **Token is required.**

### Retrieve User

Use `GET api/user/user/{int}` to retrieve a user by its primary key. **Token is optional.**

### Retrieve Current User 

Use `GET api/user/user/me` to retrieve a current user. **Token is required.**

### Update User

Use `PUT api/user/user/{int}` or `PATCH api/user/user/{int}` to update a user. **Token is required.**

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

## Email Preference

### Retrieve email preference

Use `GET api/user/email-preference/{int}` to retrieve an email preference by its primary key. **Token is required** and **must be owner.**

### Retrieve own email preference

Use `GET api/user/email-preference/me` to retrieve an email preference of the current user. **Token is required.**

### Update email preference

Use `PUT api/user/email-preference/{int}` or `PATCH api/user/email-preference/{int}` to update an email preference. **Token is required** and **must be owner.**

```json
{
    "receive_own_club": "boolean",
    "receive_own_event": "boolean",
    "receive_own_lab": "boolean",
    "receive_other_events": "boolean",
}
```
