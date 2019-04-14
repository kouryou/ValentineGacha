import json
import logging
import os
from slackclient import SlackClient
import random
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
    presenter_user_id = [user["id"] for user in users
                         if user["profile"]["real_name"] == event["name"]]

    # 当選者を選ぶ
    winners = select_winners(event, users)

    # 当選者のID一覧を取得
    winners_id = get_winners_id(winners)

    # 当選者の名前一覧を取得
    winners_name = get_winners_name(winners)

    # チョコをあげる人と当選者のチャンネル作成
    new_channel_id = create_winners_and_presenter_channel(event)

    # 新チャンネルにチョコあげる人と当選者を招待
    invite_new_channel(new_channel_id, presenter_user_id, winners_id)

    # 新チャンネルを退会
    leave_new_channel(new_channel_id)

    # レスポンス作成
    response = create_response(new_channel_id, winners_name)

    return response


# ユーザー一覧取得
def get_users_list():
    # ワークスペースのユーザー一覧を取得
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

    # チョコあげる人取得
    exist_user = [user for user in users
                  if user["profile"]["real_name"] == event["name"]]
    # チョコあげる人がワークスペースにいないユーザの場合エラー
    if not exist_user:
        return "Invalid user"


# 当選者を選ぶ
def select_winners(event, users):
    # 対象外のユーザーを除外
    excluded_users = []
    applicable_users = [user for user in users
                        if not user["id"] in excluded_users]

    # ランダムでユーザー選択
    winners = random.sample(applicable_users, event["number"])
    return winners


# 当選者のID一覧を取得
def get_winners_id(winners):
    # 当選者のID一覧を作成
    winners_id = [winner["id"] for winner in winners]

    # 当選者のIDをログ出力
    logger = logging.getLogger()
    logger.warn(winners_id)

    return winners_id


# 当選者の名前の一覧を取得
def get_winners_name(winners):
    # 当選者の名前一覧を作成
    winners_name = [winner["profile"]["real_name"] for winner in winners]

    # 当選者名をログ出力
    logger = logging.getLogger()
    logger.warn(winners_name)

    return winners_name


# チョコあげる人と当選者のチャンネル作成
def create_winners_and_presenter_channel(event):
    # チャンネル名が被らないように、ランダム文字列作成
    random_str = "".join([random.choice(string.digits) for i in range(5)])

    # チャンネル名作成
    group_name = "当選者と" + event["name"] + "-" + random_str
    # チャンネル作成
    created_group = sc_user.api_call(
        "groups.create",
        name=group_name
    )

    # チャンネルID取得
    return created_group["group"]["id"]


# 新チャンネルにチョコあげる人と当選者を招待
def invite_new_channel(new_channel_id, presenter_user_id, winners_id):
    # チョコあげる人と当選者の一覧作成
    winners_id.append(presenter_user_id)

    # 新チャンネルに招待
    for winner_id in winners_id:
        sc_user.api_call(
            "groups.invite",
            channel=new_channel_id,
            user=winner_id
        )


# 新チャンネルを退会
def leave_new_channel(new_channel_id):
    sc_user.api_call(
        "groups.leave",
        channel=new_channel_id
    )


# レスポンス作成
def create_response(new_channel_id, winners_name):
    # 新チャンネルのURLを作成
    new_channel_url = os.environ["VALENTINE_GACHA_URL"] + new_channel_id

    # レスポンス作成
    response = {
        "name": winners_name,
        "url": new_channel_url
    }

    return response