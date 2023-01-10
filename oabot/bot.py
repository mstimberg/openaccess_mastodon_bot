import logging
import os

from mastodon import Mastodon, StreamListener

from .post import create_replies


class BotListener(StreamListener):
    def __init__(self, client:Mastodon):
        self.client = client
        self.logger = logging.getLogger(__name__)

    def on_notification(self, notification:dict):
        if notification.get('type', '') == 'follow':
            self.logger.debug(f'following back {notification["account"]["url"]}')
            self.follow_back(notification)

    def on_update(self, status:dict):
        replies = create_replies(status['content'])
        if replies:
            self.logger.debug(f"Will reply to post {status['url']}")
            reply_to = status
            for idx, reply in enumerate(replies):
                reply_to = self.client.status_reply(reply_to, reply, untag=(idx == 0))  # untagging first reply only
                self.logger.debug(f"Reply {idx+1}/{len(replies)} posted as {reply_to['url']}")

    def follow_back(self, notification:dict):
        # TODO: What about #nobot?
        self.client.account_follow(notification['account']['id'])
        self.logger.debug(f'account followed! {notification["account"]["url"]} with id {notification["account"]["id"]}')


class Bot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        api_url = os.environ.get('MASTO_URL', 'http://mastodon.local')
        self.logger.debug(f"Initializing Mastodon client for {api_url}")
        self.client = Mastodon(
            access_token=os.environ.get('MASTO_TOKEN'),
            api_base_url=api_url,
            version_check_mode='none'
        )
        app = self.client.app_verify_credentials()
        self.logger.debug(f"App info: {app}")
        self.listener = BotListener(self.client)

    def start_stream(self):
        self.logger.debug('Start listening to stream')
        self.client.stream_user(
            listener=self.listener,
        )


