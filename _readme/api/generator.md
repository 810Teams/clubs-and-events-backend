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
- If the QR code for a certain event already exists, a status code of `400` will be returned.

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
- If the join key for a certain event already exists, a status code of `400` will be returned.

### Delete Join Key

`DELETE api/generator/join-key/{int}`

- Token is required.
- The current user must be a deputy leader of the event that the join key in created in.

### Generate Join Key

`GET api/generator/join-key/generate`

#### URL Parameters

`length={int}` must be an integer from 8 to 64, by leaving blank, 32 will be used as default.

### Use Join Key

`POST api/generator/join-key/use`

```json
{
    "key": "string"
}
```

- Token is required.
- If the join key is not provided, a status code of `400` will be returned.
- If the user is already a member, a status code of `400` will be returned.
- If the join key does not exist, a status code of `404` will be returned.

## Generated Microsoft Word Document

### List Generated Microsoft Word Documents

`GET api/generator/docx`

- Token is required.
- Only generated Microsoft Word documents created in the club the current user is the vice president will be shown.

#### URL Parameters

`club={int}`

`advisor={int}`

### Retrieve Generated Microsoft Word Document

`GET api/generator/docx/{int}`

- Token is required.
- The current user must be a vice president of the club that the generated Microsoft Word document in created in.

### Create Generated Microsoft Word Document

`POST api/generator/docx`

```json
{
    "objective": "string",
    "objective_list": "string",
    "room": "string",
    "schedule": "string",
    "plan_list": "string",
    "merit": "string",
    "club": "int",
    "advisor": "int"
}
```

- Token is required.
- The field `objective` and `room` must be a single line, otherwise, a status code of `400` will be returned.
- The current user must be a vice president of the club that the generated Microsoft Word document in created in, otherwise, a status code of `400` will be returned.
- The advisor must be a lecturer, otherwise, a status code of `400` will be returned.
- If the generated Microsoft Word document for a certain club already exists, a status code of `400` will be returned.

### Update Generated Microsoft Word Document

`PUT api/generator/docx/{int}`

`PATCH api/generator/docx/{int}`

```json
{
    "objective": "string",
    "objective_list": "string",
    "room": "string",
    "schedule": "string",
    "plan_list": "string",
    "merit": "string",
    "advisor": "int"
}
```

- Token is required.
- The field `objective` and `room` must be a single line, otherwise, a status code of `400` will be returned.
- The current user must be a vice president of the club that the generated Microsoft Word document in created in.
- The advisor must be a lecturer, otherwise, a status code of `400` will be returned.

### Delete Generated Microsoft Word Document

`DELETE api/generator/docx/{int}`

- Token is required.
- The current user must be a president of the club that the generated Microsoft Word document in created in.
