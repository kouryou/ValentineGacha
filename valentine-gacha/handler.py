import json
import logging
import os
from slackclient import SlackClient
import random


def select_random_user(event, context):

    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    users = sc.api_call(
        "users.list"
    )
    members = users["members"]
    random_user = random.choice(members)

    selected_user_name = random_user["profile"]["real_name"]

    logger = logging.getLogger()
    logger.warn(selected_user_name)

    response = {
        "name": selected_user_name
    }

    return response
