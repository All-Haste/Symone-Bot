# Symone Bot

Symone Bot is a slack bot built with Python and run on Google Cloud Functions (with GCP Datastore backing).

## Commands and Aspects

The bulk of functionality is implemented via a system of Commands that perform actions on Aspects. A command could be
something like `add`, while an aspect could be something like experience points or `xp`. So when a user invokes Symone
Bot with `Symone, add xp 1000` it triggers an add `Command` to add 1000 to the `xp` aspect.

## Parser

Symone Bot uses a simple recursive descent parser, located in `symone_bot/parser.py` to "understand" user input. The main area this is used is to understand "aspect" queries.


## Cloud Resources and Deployment

The bot is deployed to GCP Cloud Functions, and uses GCP Datastore as a backing store. Deployment is handled via the Github Release action.

### Other Stuff

The bot is reached via https://us-central1-sixth-impulse-322819.cloudfunctions.net/symone_bot/
