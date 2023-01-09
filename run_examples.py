import sys

# Quick and dirty path fiddling
sys.path.insert(0, ".")

from oabot.extract import EMAIL
from oabot.post import create_replies

if __name__ == "__main__":
    if EMAIL is None:
        raise TypeError(
            "Set the EMAIL environment variable to your email "
            "address for polite usage of the APIs."
        )
    test_text = """
<p>A fake Mastodon post</p>
<p>Here's an <a href='https://doi.org/10.1016/j.tics.2021.03.018'>
interesting article</a>!"""
    print(test_text)
    print()
    print(create_replies(test_text)[0])
    print()
    test_text_2 = """
<p>Here's another post with multiple URLs in it:</p>
<p>This one is a <a href="https://doi.org/10.1016/j.tics.2021.03.018">DOI</a> and
this one is a <a href="https://www.nature.com/articles/s41583-018-0038-8">URL</a>.</p>
<p>Both are closed access, the first one has a preprint and the second one a postprint.</p>"""
    print()
    for reply in create_replies(test_text_2):
        print(reply)
