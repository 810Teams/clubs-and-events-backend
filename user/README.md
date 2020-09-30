# User Application API Endpoints

## Login

Use `POST api/user/login` to request a token.

```json
{
    "username": string,
    "password": string
}
```

## User

### List All Users

Use `GET api/user/user` to list all users. This does not require a token, but with a token will show more detailed user information.

`search={string}` to search for username, name, or nickname.

`is_active={boolean}` to filter for active users. Requires a token.

`is_staff={boolean}` to filter for staff. Requires a token.

`is_superuser={boolean}` to filter for superusers. Requires a token.

### Retrieve User

Use `GET api/user/user/{int}` to retrieve a user by its primary key. This does not require a token, but with a token will show more detailed user information.

### Retrieve Current User

Use `GET api/user/user/me` to retrieve a current user. Requires a token.

### Update User

`PUT api/user/user/{int}`
`PATCH api/user/user/{int}`

```json
{
    "id": int,
    "username": string,
    "name": string,
    "email": string,
    "nickname": string,
    "bio": string,
    "profile_picture": image,
    "cover_photo": image,
    "birthdate": date,
}
```
