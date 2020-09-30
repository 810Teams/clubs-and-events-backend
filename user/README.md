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

### List All Users ![](https://img.shields.io/badge/Optional-Token-blue)

Use `GET api/user/user` to list all users. This does not require a token, but with a token will show more detailed user information.

`search={string}` to search for username, name, or nickname.

`is_active={boolean}` to filter for active users. ![](https://img.shields.io/badge/Requires-Token-orange)

`is_staff={boolean}` to filter for staff. ![](https://img.shields.io/badge/Requires-Token-orange)

`is_superuser={boolean}` to filter for superusers. ![](https://img.shields.io/badge/Requires-Token-orange)

### Retrieve User ![](https://img.shields.io/badge/Optional-Token-blue)

Use `GET api/user/user/{int}` to retrieve a user by its primary key. This does not require a token, but with a token will show more detailed user information.

### Retrieve Current User ![](https://img.shields.io/badge/Requires-Token-orange)

Use `GET api/user/user/me` to retrieve a current user.

### Update User ![](https://img.shields.io/badge/Requires-Token-orange)

Use `PUT api/user/user/{int}` or `PATCH api/user/user/{int}` to update a user.

```json
{
    "id": "int",
    "username": "string",
    "name": "string",
    "email": "string",
    "nickname": "string",
    "bio": "string",
    "profile_picture": "image",
    "cover_photo": "image",
    "birthdate": "date",
}
```
