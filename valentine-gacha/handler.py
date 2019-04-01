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
slack_user_token = os.environ["SLACK_USER_TOKEN"]

# SlackClient作成
sc_bot = SlackClient(slack_bot_token)
sc_user = SlackClient(slack_user_token)


def select_random_user(event, context):
    # ユーザー一覧を取得
    users = get_users_list()

    # バリデーション
    validation_message = validate(event, users)
    if validation_message is not None:
        return {"message": validation_message}

    # チョコあげる人のユーザID
    presenter_user_id = filter(lambda user: user["profile"]["real_name"] == event["name"], users)

    # 当選者を選ぶ
    winners = select_winners(event, users)

    # slack通知
    notice_to_slack(event, winners)

    # 当選者のID一覧を取得
    winners_id = get_winners_id(winners)

    # 当選者の名前一覧を取得
    winners_name = get_winners_name(winners)

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
    winners_id.append(presenter_user_id)
    # 新規グループに招待
    for winner_id in winners_id:
        sc_user.api_call(
            "groups.invite",
            channel=group_id,
            user=winner_id
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


# 当選者を選ぶ
def select_winners(event, users):
    # 対象外のユーザーを除外
    excluded_users = []
    applicable_users = [user for user in users if not user["id"] in excluded_users]

    # ランダムでユーザー選択
    winners = random.sample(applicable_users, event["number"])
    return winners


# 当選者のID一覧を取得
def get_winners_id(winners):
    # 当選者のID一覧を作成
    winners_id = []

    for winner in winners:
        # 当選者のID一覧作成
        winners_id.append(winner["id"])

    # 当選者のIDをログ出力
    logger = logging.getLogger()
    logger.warn(winners_id)

    return winners_id


# 当選者の名前の一覧を取得
def get_winners_name(winners):
    winners_name = []

    for winner in winners:
        # 当選者の名前一覧作成
        winners_name.append(winner["profile"]["real_name"])

    # 当選者名をログ出力
    logger = logging.getLogger()
    logger.warn(winners_name)

    return winners_name


# slack通知
def notice_to_slack(event, winners):
    # 当選者のメンションと名前の一覧を作成
    winners_mention = ""
    for winner in winners:
        # 当選者のメンション一覧作成
        mention = "<@" + winner["id"] + ">さん\n"
        winners_mention += mention

    # 通知用メッセージ組み立て
    send_text = "*" + event["name"] + "* です :heart: \n" + winners_mention + "よかったらチョコ受けとってくれると嬉しいな :two_hearts:"

    # メッセージ画像取得
    image = urllib.request.urlopen(os.environ["MESSAGE_IMAGE_URL"]).read()

    # slack通知
    sc_bot.api_call(
        "files.upload",
        initial_comment=send_text,
        file=image,
        channels=notice_channel
    )
