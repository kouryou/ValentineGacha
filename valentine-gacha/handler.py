import json
import logging
import os
from slackclient import SlackClient
import random
import urllib.request
import string


def select_random_user(event, context):

    # 環境変数読み込み
    notice_channel = os.environ["SLACK_NOTICE_CHANNEL"]
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

    # SlackClient作成
    sc_bot = SlackClient(slack_bot_token)

    # ユーザー一覧取得
    users_list_response = sc_bot.api_call(
        "users.list"
    )

    # レスポンスからユーザー情報を抽出
    users = users_list_response["members"]

    # TODO: バリデーション

    # 対象外のユーザーを除外(Bot, 運営者)
    # TODO: 運営者を削除
    excluded_users = ["USLACKBOT", "UG2Q80MFE"]
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
        mention = "<@" + selected_user["id"] + ">\n"
        selected_users_mention += mention
        # 当選者の名前一覧作成
        selected_users_name.append(selected_user["profile"]["real_name"])

    # 選ばれたユーザー情報をログ出力
    logger = logging.getLogger()
    logger.warn(selected_users_mention)
    logger.warn(selected_users_name)

    # 通知用メッセージ組み立て
    send_text = selected_users_mention + "<@" + event["name"] + "> さんがチョコあげるって :chocolate_bar: \n私からじゃないからね！"

    # メッセージ画像取得
    image = urllib.request.urlopen('https://s3-ap-northeast-1.amazonaws.com/valentine-gacha-image/valentine.jpg').read()

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
    for i in range(10):
        random_str += random.choice(string.digits + string.ascii_letters)

    # グループ名作成
    group_name = "当選者と女神様-" + random_str
    # グループ作成
    created_group = sc_user.api_call(
        "groups.create",
        name=group_name
    )
    #グループID取得
    group_id = created_group["group"]["id"]

    # チョコをあげる人と当選者の一覧作成
    group_members = selected_users_id.append(event["name"])
    # 新規グループに招待
    for group_member in group_members:
        sc_user.api_call(
            "groups.invite",
            channel=group_id,
            user=group_member
        )

    # レスポンス作成
    response = {
        "name": selected_users_name
    }

    return response
