# Design Guide - Index

## Club Tab
The club tab is where all clubs reside. A separator between official clubs and unofficial clubs is required if the user is authenticated and at least one unofficial club is received from the API.

If the user is not authenticated, any unofficial clubs and non-publicly visible clubs will be automatically filtered out by the API.

### List Official Clubs

`GET api/community/club?is_official=1`

### List Unofficial Clubs

`GET api/community/club?is_official=0`

## Event Tab
The event tab is where all events reside. No separator is needed, but an API is needed to be called twice.

If the user is not authenticated, any unapproved events and non-publicly visible events will be automatically filtered out by the API.

### List Events

`GET api/community/event`

### List Community Events

`GET api/community/event/community`

## Lab Tab
The lab tab is where all labs reside. Just call an API and everything is done.

If the user is not authenticated, any non-publicly visible labs will be automatically filtered out by the API.

### List Labs

`GET api/community/lab`
