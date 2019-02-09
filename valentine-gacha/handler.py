import json
import logging
import os
from slackclient import SlackClient
import random


def select_random_user(event, context):

    # 環境変数読み込み
    notice_channel = os.environ["SLACK_NOTICE_CHANNEL"]
    slack_token = os.environ["SLACK_API_TOKEN"]

    # SlackClient作成
    sc = SlackClient(slack_token)

    # ユーザー一覧取得
    users_list_response = sc.api_call(
        "users.list"
    )

    # レスポンスからユーザー情報を抽出
    users = users_list_response["members"]

    # 対象外のユーザーを除外
    applicable_users = [user for user in users if not user["id"] == "USLACKBOT"]

    # ランダムで一人選択
    selected_users = random.sample(applicable_users, event["number"])

    # 当選者のメンションと名前の一覧を作成
    selected_users_name = ""
    selected_users_mention = ""
    for selected_user in selected_users:
        # 当選者のメンション一覧作成
        mention = "<@" + selected_user["id"] + ">\n"
        selected_users_mention += mention
        # 当選者の名前一覧作成
        formatted_user_name = "*" + selected_user["profile"]["real_name"] + "*" + "\n"
        selected_users_name += formatted_user_name

    # 選ばれたユーザー情報をログ出力
    logger = logging.getLogger()
    logger.warn(selected_users_mention)
    logger.warn(selected_users_name)

    # 通知用メッセージ組み立て
    send_text = selected_users_mention + "*" + event["name"] + "* さんからのチョコ :chocolate_bar: \n選ばれたのは、\n" + selected_users_name + "でした。 :tea:"

    # slack通知
    sc.api_call(
        "chat.postMessage",
        channel=notice_channel,
        text=send_text
    )

    # レスポンス作成
    response = {
        "name": selected_users_name
    }

    return response
