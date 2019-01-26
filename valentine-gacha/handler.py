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
    selected_user = random.choice(applicable_users)

    # メッセージに必要なユーザー情報格納
    selected_user_name = selected_user["profile"]["real_name"]
    selected_user_id = selected_user["id"]

    # 選ばれたユーザー情報をログ出力
    logger = logging.getLogger()
    logger.warn(selected_user_name)
    logger.warn(selected_user_id)

    # 通知用メッセージ組み立て
    send_text = "<@" + selected_user_id + ">\n*" + event["name"] + "* さんからのチョコ :chocolate_bar: \n選ばれたのは、 *" + selected_user_name + "* でした。 :tea:"

    # slack通知
    sc.api_call(
        "chat.postMessage",
        channel=notice_channel,
        text=send_text
    )

    # レスポンス作成
    response = {
        "name": selected_user_name
    }

    return response
