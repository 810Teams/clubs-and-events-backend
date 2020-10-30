# User Application API Endpoints

## Login

`POST api/user/login`

```json
{
    "username": "string",
    "password": "string"
}
```

- Returns a token if the credentials are valid.

## User

### List Users

`GET api/user/user`

- Token is optional.
- If the token is present, more detailed user data will be shown.

#### URL Parameters

`search={string}`

`user_group={string}`

`is_active={boolean}`

`is_staff={boolean}`

`is_superuser={boolean}`

`is_applicable_for={int}` when `{int}` is the community ID.

### Retrieve User

`GET api/user/user/{int}`

- Token is optional.
- If the token is present, more detailed user data will be shown.

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
    "birthdate": "date"
}
```

- Token is required.
- Must be the owner.

## Email Preference

### Retrieve Email Preference

`GET api/user/email-preference/{int}`


- Token is required
- Must be the owner.

### Retrieve Own Email Preference

`GET api/user/email-preference/me`

- Token is required.

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

- Token is required
- Must be the owner.

## Student Committee Authority

### List Student Committee Authorities

`GET api/user/student-committee`

- Token is required

### Retrieve Student Committee Authority

`GET api/user/student-committee/{int}`

- Token is required

### Retrieve Own Student Committee Authority

`GET api/user/student-committee/me`

- Token is required
