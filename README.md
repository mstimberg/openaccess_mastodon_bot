# Open-access mastodon bot

**Work-in-progress, do not use**

A Mastodon bot to reply to threads mention closed access URLs to papers with
open access alternatives.

Created for https://neuromatch.social

Relies on https://unpaywall.org and https://www.crossref.org

Install with (if not using the docker container below):
```
pip install .
```
## Running the bot for local testing

Run your local Mastodon instance, e.g. by installing latest versions of vagrant and VirtualBox, and then:
```
$ vagrant up
$ vagrant ssh -c "cd /vagrant && foreman start" 
```

On your instance, add a new account for the bot and create a new application for it.

Put the *access token* into an environment variable `MASTO_TOKEN`, and your email address into `EMAIL` (for "polite" access to the APIs).

### Running with Docker
Build the docker container in this repo:
```
$ docker build -t mastodon_bot .
```

Start the docker container to run the bot
```
$ docker run docker run --network host -e MASTO_TOKEN -e EMAIL mastodon_bot
```

### Running without Docker

Start the bot with
```
$ python -m oabot
```

### Function

Now, if you follow the bot account, it should follow you back.
If you post a status with a closed access URL in it, it will reply with an open access version (if it can find one).

## Basic testing
Run tests:
```
pytest oabot/tests
```

Run an example with fake Mastodon posts (note that specifying your email is 
necessary for "polite" usage of the APIs):
```
EMAIL=your_email@example.com python run_examples.py
```

Run on an existing Mastodon post by specifying the status ID:
```commandline
EMAIL=your_email@example.com python run_mastodon.py STATUS_ID
```