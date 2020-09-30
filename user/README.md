# User Application API Endpoints

## Login

`POST api/user/login`

```json
{
    "username": "string",
    "password": "string"
}
```

- Returns a token

## User

### List All Users

`GET api/user/user`

- Token is optional, if presents, more detailed user data will be shown.

#### URL Parameters

`search={string}`

`is_active={boolean}`

`is_staff={boolean}`

`is_superuser={boolean}`

### Retrieve User

`GET api/user/user/{int}`

- Token is optional, if presents, more detailed user data will be shown.

### Retrieve Current User 

`GET api/user/user/me`

### Update User

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

- Token is required, and must be the owner.

## Email Preference

### Retrieve Email Preference

`GET api/user/email-preference/{int}`


- Token is required, and must be the owner.

### Retrieve Own Email Preference

Use `GET api/user/email-preference/me`

- Token is required

### Update Email Preference

`PUT api/user/email-preference/{int}`

`PATCH api/user/email-preference/{int}`

```json
{
    "receive_own_club": "boolean",
    "receive_own_event": "boolean",
    "receive_own_lab": "boolean",
    "receive_other_events": "boolean",
}
```

- Token is required, and must be the owner.
