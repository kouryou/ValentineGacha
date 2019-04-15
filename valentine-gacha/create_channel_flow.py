import os
import random
import string
from slackclient import SlackClient


sc_user = SlackClient(os.environ["SLACK_USER_TOKEN"])


# ハンドラ関数
def handler(event, context):
    # チョコあげる人のユーザID
    presenter_id = event["presenter_id"]
    # 当選者のユーザID
    winners_id = event["winners_id"]

    # チャンネル作成のフローを実行
    response = execute_create_channel_flow(presenter_id, winners_id)

    return response


# チャンネル作成のフローを実行
def execute_create_channel_flow(presenter_id, winners_id):
    # チョコをあげる人と当選者のチャンネル作成
    new_channel_id = create_winners_and_presenter_channel()

    # 新チャンネルにチョコあげる人と当選者を招待
    invite_new_channel(new_channel_id, presenter_id, winners_id)

    # 新チャンネルを退会
    leave_new_channel(new_channel_id)

    # レスポンス作成
    response = create_response(new_channel_id)

    return response


# チョコあげる人と当選者のチャンネル作成
def create_winners_and_presenter_channel():
    # チャンネル名が被らないように、ランダム文字列作成
    random_str = "".join([random.choice(string.digits) for i in range(6)])

    # チャンネル名作成
    group_name = "バレンタインガチャ当選ルーム-" + random_str
    # チャンネル作成
    created_group = sc_user.api_call(
        "groups.create",
        name=group_name
    )

    # チャンネルID取得
    return created_group["group"]["id"]


# 新チャンネルにチョコあげる人と当選者を招待
def invite_new_channel(new_channel_id, presenter_id, winners_id):
    # チョコあげる人と当選者の一覧作成
    new_channel_members = winners_id + [presenter_id]

    # 新チャンネルに招待
    for new_channel_member in new_channel_members:
        sc_user.api_call(
            "groups.invite",
            channel=new_channel_id,
            user=new_channel_member
        )


# 新チャンネルを退会
def leave_new_channel(new_channel_id):
    sc_user.api_call(
        "groups.leave",
        channel=new_channel_id
    )


# レスポンス作成
def create_response(new_channel_id):
    # 新チャンネルのURLを作成
    new_channel_url = os.environ["VALENTINE_GACHA_URL"] + new_channel_id

    # レスポンス作成
    response = {
        "new_channel_url": new_channel_url
    }

    return response