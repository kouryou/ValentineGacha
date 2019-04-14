import logging
import os
from slackclient import SlackClient
import random


def select_random_user(event, context):
    # ユーザー一覧を取得
    users = get_users_list()

    # バリデーション
    validation_message = validate(event, users)
    if validation_message is not None:
        return {"message": validation_message}

    # チョコあげる人のユーザID
    presenter_id = event["presenter_id"]

    # 当選者を選ぶ
    winners = select_winners(event, users)

    # レスポンス作成
    response = create_response(winners)

    return response


# ユーザー一覧取得
def get_users_list():
    # SlackClient作成
    sc_bot = SlackClient(os.environ["SLACK_BOT_TOKEN"])

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
                  if user["id"] == event["presenter_id"]]
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


# レスポンス作成
def create_response(winners):
    # レスポンス用に当選者の情報を加工
    serialized_winners_data = serialize_winners_data(winners)

    # レスポンス作成
    response = {
        "winners": serialized_winners_data
    }

    return response


# 当選者の情報を加工
def serialize_winners_data(winners):
    # 当選者のidと名前を抽出
    serialized_winners_data = [
        {
            "id": winner["id"],
            "name": winner["profile"]["real_name"]
        }
        for winner in winners]

    # 当選者情報をログ出力
    logger = logging.getLogger()
    logger.warn(serialized_winners_data)

    return serialized_winners_data