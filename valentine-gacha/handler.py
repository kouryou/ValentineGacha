import json
import logging
import os
from slackclient import SlackClient
import random
import urllib.request
import string


# 環境変数読み込み
notice_channel = os.environ["SLACK_NOTICE_CHANNEL"]
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
# SlackClient作成
sc_bot = SlackClient(slack_bot_token)

#
def select_random_user(event, context):
    # ユーザー一覧を取得
    users = get_users_list()

    # バリデーション
    validation_message = validate(event, users)
    if validation_message is not None:
        return {"message": validation_message}

    # チョコあげる人のユーザID
    presenter_user_id = filter(lambda user: user["profile"]["real_name"] == event["name"], users)

    # 対象外のユーザーを除外
    excluded_users = []
    applicable_users = [user for user in users if not user["id"] in excluded_users]

    # ランダムでユーザー選択
    selected_users = random.sample(applicable_users, event["number"])

    # 当選者のメンションと名前の一覧を作成
    selected_users_name = []
    selected_users_id = []
    selected_users_mention = ""
    for selected_user in selected_users:
        # 当選者のID一覧作成
        selected_users_id.append(selected_user["id"])
        # 当選者のメンション一覧作成
        mention = "<@" + selected_user["id"] + ">さん\n"
        selected_users_mention += mention
        # 当選者の名前一覧作成
        selected_users_name.append(selected_user["profile"]["real_name"])

    # 選ばれたユーザー情報をログ出力
    logger = logging.getLogger()
    logger.warn(selected_users_mention)
    logger.warn(selected_users_name)

    # 通知用メッセージ組み立て
    send_text = "*" + event["name"] + "* です :heart: \n" + selected_users_mention + "よかったらチョコ受けとってくれると嬉しいな :two_hearts:"

    # メッセージ画像取得
    image = urllib.request.urlopen(os.environ["MESSAGE_IMAGE_URL"]).read()

    # slack通知
    sc_bot.api_call(
        "files.upload",
        initial_comment=send_text,
        file=image,
        channels=notice_channel
    )

    # 環境変数読み込み
    slack_user_token = os.environ["SLACK_USER_TOKEN"]
    # SlackClient作成
    sc_user = SlackClient(slack_user_token)

    # グループ名作成用ランダム文字列
    random_str = ""
    for i in range(5):
        random_str += random.choice(string.digits)

    # グループ名作成
    group_name = "当選者と" + event["name"] + "-" + random_str
    # グループ作成
    created_group = sc_user.api_call(
        "groups.create",
        name=group_name
    )
    # グループID取得
    group_id = created_group["group"]["id"]

    # チョコをあげる人と当選者の一覧作成
    selected_users_id.append(presenter_user_id)
    # 新規グループに招待
    for selected_user_id in selected_users_id:
        sc_user.api_call(
            "groups.invite",
            channel=group_id,
            user=selected_user_id
        )

    # グループ退会
    sc_user.api_call(
        "groups.leave",
        channel=group_id
    )

    new_channel_url = os.environ["VALENTINE_GACHA_URL"] + group_id

    # レスポンス作成
    response = {
        "name": winners_name,
        "url": new_channel_url
    }

    return response

# ユーザー一覧取得
def get_users_list():
    users_list_response = sc_bot.api_call(
        "users.list"
    )

    # レスポンスからユーザー情報を抽出
    return users_list_response["members"]

# バリデーション
def validate(event, users):
    # 指定人数がチョコ欲しい人を超えていた場合エラー
    if event["number"] > len(users):
        return "Invalid number"

    # チョコあげる人がワークスペースにいないユーザの場合エラー
    exist_flg = False
    for user in users:
        if user["profile"]["real_name"] == event["name"]:
            return None

    return "Invalid user"