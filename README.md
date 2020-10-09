# Excel-To-Google-Calendar
### About
this project is made in order to automate my schedule, I wanted to keep in touch with all friends,
friends that you talk to once every three week type.
I was afraid that it will look robotic and unreal, so I created this project in order to randomize the call list.

## Description
This code takes the names from an xlsx file and generates and 
There is an excel file (here it is just an example) so it will be easy to edit the names in a table.
the code uses the google-calendar API in order to add the events to my calendar.
keep in mind that you need to allow the code to use your google account.

### Prerequisites
you need to use the google-api and download all the libaraies pip:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
you can get all the info from https://developers.google.com/calendar/quickstart/python

**Before Using**
1. Enter your names and dates of last talk to the file
2. update the conf.json to your data

## Authors
 **Ido Ziv**
