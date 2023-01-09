import sys

# Quick and dirty path fiddling
sys.path.insert(0, ".")
import logging

from mastodon import Mastodon

from oabot.post import create_replies
from oabot.extract import EMAIL


if __name__ == "__main__":
    if EMAIL is None:
        raise TypeError(
            "Set the EMAIL environment variable to your email "
            "address for polite usage of the APIs."
        )
    if len(sys.argv) != 2:
        raise ValueError("Need to provide a Mastodon status ID")
    try:
        status_id = int(sys.argv[1])
    except ValueError:
        raise ValueError("Mastodon status ID must be an integer")
    m = Mastodon(api_base_url="https://neuromatch.social")
    replies = create_replies(m.status(status_id).content)
    if not replies:
        print("No replies to be made")
    else:
        for line in replies:
            print(line)
