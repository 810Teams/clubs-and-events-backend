# Design Guide - Community Page (Generate Document Menu)

## Generate Document Menu

In the club, vice presidents and the president of the club can access this menu via the menu selection of the club header, or via the link in the approval request form page.

The purpose of this menu is to allow vice presidents and the president of the club to generate a document used in registering and renewing the club.

### Check if the Form Exists

First, check if the generated Microsoft Word document of the club exists by calling this API.

`GET api/generator/docx?club={int}`

The `{int}` is the ID of the club.

If the result is an empty list, render a single button saying something like "Generate Document", which display the form upon click.

### Submitting the Form

After the form appears, users can fill the form. Upon the user clicked "Generate", perform one of these actions depends on the existing object.

If the object does not exist, call this API. The field `club` must be auto.

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

If the object already exist, call one of these APIs.

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

### Deleting the Generated Microsoft Word Document

If the object exists, render the delete button. Upon the user clicked the button, display a confirmation dialog, if the user confirmed, call this API.

`DELETE api/generator/docx/{int}`
