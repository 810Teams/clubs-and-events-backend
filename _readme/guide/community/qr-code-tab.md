# Design Guide - Community Page (QR Code Tab)

## QR Code Tab

The QR code tab is the 6th tab next to the requests tab. Members can view the QR code in this tab, while deputy leaders can create or delete it. This tab only exists in the events and community events. 

### Retrieving QR Code

First of all, call this API to retrieve QR code.

`GET api/generator/qr-code?community={int}`

The `{int}` is the ID of the community.

- If it returns an empty list, render the [create QR code button](#rendering-create-qr-code-button).
- If it returns a list with a single item, display it, and render the [delete and regenerate QR code buttons](#rendering-delete-and-regenerate-qr-code-buttons).

### Rendering Create QR Code Button

The create QR code buttom must be rendered if the event currently does not have an existing QR code. Based on the event type, call one of these APIs.

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

The field `own_membership_position` is expected, if at least `2`, and the [previous result](#retrieving-qr-code) is an empty list, render the button.

### Create QR Code

First, generate a random string to use as a join key by calling this API. The default length is 32.

`GET api/generator/join-key/generate`

Next, use the generated string that was just generated to create a join key.

`POST api/generator/join-key`

```json
{
    "key": "string",
    "event": "int"
}
```

The `key` is a random string consist of alphabetical characters and numbers, with the length not more than 64 character. The event must be auto.

Then, create the QR code.

`POST api/generator/qr-code`

```json
{
    "url": "string",
    "event": "int"
}
```

The URL and the event must be auto. The URL must be the URL that activates the join key, meaning, the join key must be embedded in the URL.

For example, if the key is `UwD3hIolrTAgKV62`, the URL that will be used to generate the QR code should be something like `https://community.it.kmitl.ac.th/join/UwD3hIolrTAgKV62` or `https://community.it.kmitl.ac.th/join?key=UwD3hIolrTAgKV62`.

### Using the Join Key

Upon the user calls one of these two URLs, whether via QR code or pasting the URL directly, the front-side must retrieve the key from the URL, then call this API with the key sent as data.

`POST api/generator/join-key/use`

```json
{
    "key": "string"
}
```

### Rendering Delete and Regenerate QR Code Buttons

The delete and regenerate QR code buttons are always together. These 2 buttons must be rendered if the event currently has an existing QR code. Based on the event type, call one of these APIs.

`GET api/community/event/{int}`

`GET api/community/event/community/{int}`

The field `own_membership_position` is expected, if at least `2`, and the [previous result](#retrieving-qr-code) is not an empty list, render both buttons.

### Delete QR Code

Deleting the QR code also means disabling the join key, so delete both.

`DELETE api/generator/qr-code/{int}`

`DELETE api/generator/join-key/{int}`

### Regenerate QR Code

Users have option to regenerate QR code, so users will not be needed to delete and create them in different operations.

When the user clicked the button, repeat the steps in the [delete QR code section](#delete-qr-code), then in the [create QR code section](#create-qr-code).
