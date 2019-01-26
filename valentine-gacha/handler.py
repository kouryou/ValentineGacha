import json
import logging
import os
from slackclient import SlackClient


def random(event, context):

    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    users = sc.api_call(
        "users.list"
    )

    logger = logging.getLogger()
    logger.warn(users)

    response = {
        "body": "success"
    }

    return response
