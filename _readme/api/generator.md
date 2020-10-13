# Generator Application API Endpoints

## QR Code

### List QR Codes

`GET api/generator/qr-code`

- Token is required.
- Only QR codes created in the event the current user is the member will be shown.

#### URL Parameter

`event={int}`

`has_join_key={boolean}`

### Retrieve QR Code

`GET api/generator/qr-code/{int}`

- Token is required.
- The current user must be a member of the event that the QR code in created in.

### Create QR Code

`POST api/generator/qr-code`

```json
{
    "url": "string",
    "event": "int"
}
```

- Token is required.
- The current user must be a deputy leader of the event that the QR code in created in, otherwise, a status code of `400` will be returned.
- The value of the `url` field must be a valid format or a URL, otherwise, a status code of `400` will be returned.

### Delete QR Code

`DELETE api/generator/qr-code/{int}`

- Token is required.
- The current user must be a deputy leader of the event that the QR code in created in.

## Join Key

### List Join Keys

`GET api/generator/join-key`

- Token is required.
- Only join keys created in the event the current user is the member will be shown.

#### URL Parameter

`event={int}`

### Retrieve Join Key

`GET api/generator/join-key/{int}`

- Token is required.
- The current user must be a member of the event that the join key in created in.

### Create Join Key

`POST api/generator/join-key`

```json
{
    "key": "string",
    "event": "int"
}
```

- Token is required.
- The current user must be a deputy leader of the event that the join key in created in, otherwise, a status code of `400` will be returned.
- The value of the `key` field must only consist of alphabetical characters and numbers, otherwise, a status code of `400` will be returned.

### Delete Join Key

`DELETE api/generator/join-key/{int}`

- Token is required.
- The current user must be a deputy leader of the event that the join key in created in.
