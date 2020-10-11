# Notification Application API Endpoints

## Notification

### List Notifications

`GET api/notification/notification`

- Requires a token.
- Only shows notifications the current user is the owner.

### Retrieve Notification

`POST api/notification/notification/{int}`

- Requires a token.
- Must be an owner.

### Update Notification

`PUT api/notification/notification/{int}`

`PATCH api/notification/notification/{int}`

```json
{
    "is_read": "boolean"
}
```

- Requires a token.
- Must be an owner.

### Delete Notification

`DELETE api/notification/notification/{int}`

- Requires a token.
- Must be an owner.
