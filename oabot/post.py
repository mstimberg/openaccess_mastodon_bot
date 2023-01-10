"""
Create a post for Mastodon.
"""
from collections import defaultdict

from .extract import find_dois, annotate_dois

BOT_INTRO = """👋 I noticed that your post linked to {count} closed access article{plural}."""
BOT_SINGLE = (
    """Here's an open access {type} of {citation}: {url}"""
)


def create_replies(status: str):
    """Check the status for URLs and reply with open access variants of those
    URLs if relevant."""
    dois = find_dois(status)
    if not dois:
        return  # nothing to do
    annotated = annotate_dois(dois)
    filtered = [
        a for a in annotated if a is not None and not a["is_oa"] and "oa_url" in a
    ]
    if len(filtered) == 0:
        return  # All URLs are already open access or cannot be analyzed
    if len(filtered) == 1:
        return [create_single_reply(filtered[0])]
    else:
        return create_multiple_replies(filtered)


def format_citation(annotated: dict):
    """Format the citation for an article"""
    if len(annotated["authors"]) > 3:
        authors = ", ".join(annotated["authors"][:3]) + " et al."
    else:
        authors = ", ".join(annotated["authors"])
    return f"{authors} ({annotated['year']}). “{annotated['title']}”. {annotated['journal']}."


def create_single_reply(annotated: dict):
    """Create a reply for a single open access URL."""
    reply_text = BOT_INTRO.format(count="a", plural="")
    citation = format_citation(annotated)
    reply_text += BOT_SINGLE.format(
        type=annotated["oa_type"], citation=citation, url=annotated["oa_url"]
    )
    return reply_text


def create_multiple_replies(annotated: dict):
    """Create a reply for multiple open access URLs."""
    replies = []
    counts = {
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
        10: "ten",
        11: "eleven",
        12: "twelve",
    }
    count = counts[len(annotated)] if len(annotated) <= 12 else str(len(annotated))
    reply_text = BOT_INTRO.format(count=count, plural="s")
    reply_text += f"See the replies below for open-access versions 👇\n\n1/{len(annotated)+1}"
    replies.append(reply_text)
    for idx, a in enumerate(annotated):
        citation = format_citation(a)
        reply_text = BOT_SINGLE.format(
            type=a["oa_type"], citation=citation, url=a["oa_url"]
        )
        reply_text += f"\n\n{idx + 2}/{len(annotated)+1}"
        replies.append(reply_text)
    return replies
