Work-in-progress

A Mastodon bot to reply to threads mention closed access URLs to papers with
open access alternatives.

Created for https://neuromatch.social

Does not yet work as a bot, but can manually create replies for Mastodon posts.

Relies on https://unpaywall.org and https://www.crossref.org

Install dependencies with:
```
pip install -r requirements.txt
```

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