2016.03.29

https://developers.google.com/admin-sdk/groups-migration/v1/quickstart/python

A quick hack on the "Google Apps Groups Migration API Quickstart" program

Giving a Google Group, walk through the legacy Mailman mbox file and extract only the text/plain part and migrate to Google Groups preserving original Date.

Many scripts walk through the mbox and just forward to the google group however, that doesn't preserve the original time stamp of the message.

Multiple runs on the mbox to the Google group appear idempotent since Message-ID is constant.

At some point I may loop back to figure out how to do multi-part preservation passes since some e-mails had PDFs, M$ docs, etc.

Mac OS X 10.10.5 requires the sys.path.insert hack to work ( my dev env ) 


