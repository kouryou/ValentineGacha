import os
import random
import string
from slackclient import SlackClient


# SlackClient作成
sc_user = SlackClient(os.environ["SLACK_USER_TOKEN"])


def handler(event, context):
    """ハンドラ関数

    Parameters
    ----------
    event : dict
        イベントデータ
    context : dict
        ランタイム情報

    Returns
    -------
    dict
        作成されたチャンネルのURLを含むレスポンス
    """
    # チョコあげる人のユーザID
    presenter_id = event["presenter_id"]
    # 当選者のユーザID
    winners_id = event["winners_id"]

    # チャンネル作成のフローを実行
    response = execute_create_channel_flow(presenter_id, winners_id)

    return response


def execute_create_channel_flow(presenter_id, winners_id):
    """チャンネル作成のフローを実行

    SlackのAPIを利用して、特定のメンバーの新しいチャンネルを作成するには、
    チャンネルの作成→招待→退会(運営者アカウントが入っているため)
    という一連の流れを行う必要があるため、この関数を利用する。

    Parameters
    ----------
    presenter_id : str
        チョコあげる人のユーザID
    winners_id : str
        当選者のユーザID

    Returns
    -------
    dict
        作成されたチャンネルのURLを含むレスポンス
    """
    # チョコをあげる人と当選者のチャンネル作成
    new_channel_id = create_winners_and_presenter_channel()

    # 新チャンネルにチョコあげる人と当選者を招待
    invite_new_channel(new_channel_id, presenter_id, winners_id)

    # 新チャンネルを退会
    leave_new_channel(new_channel_id)

    # レスポンス作成
    response = create_response(new_channel_id)

    return response


def create_winners_and_presenter_channel():
    """チョコあげる人と当選者のチャンネル作成

    Returns
    -------
    str
        作成されたチャンネルのID
    """
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


def invite_new_channel(new_channel_id, presenter_id, winners_id):
    """新チャンネルにチョコあげる人と当選者を招待

    Parameters
    ----------
    new_channel_id : str
        作成されたチャンネルのID
    presenter_id : str
        チョコあげる人のユーザID
    winners_id : str
        当選者のユーザID
    """
    # チョコあげる人と当選者の一覧作成
    new_channel_members = winners_id + [presenter_id]

    # 新チャンネルに招待
    for new_channel_member in new_channel_members:
        sc_user.api_call(
            "groups.invite",
            channel=new_channel_id,
            user=new_channel_member
        )


def leave_new_channel(new_channel_id):
    """新チャンネルを退会

    新しいチャンネルに運営者アカウントが入ってしまっているため、退会する

    Parameters
    ----------
    new_channel_id : str
        作成されたチャンネルのID
    """
    sc_user.api_call(
        "groups.leave",
        channel=new_channel_id
    )


def create_response(new_channel_id):
    """レスポンス作成

    Parameters
    ----------
    new_channel_id : str
        作成されたチャンネルのID

    Returns
    -------
    dict
        作成されたチャンネルのURLを含むレスポンス
    """
    # 新チャンネルのURLを作成
    new_channel_url = os.environ["VALENTINE_GACHA_URL"] + new_channel_id

    # レスポンス作成
    response = {
        "new_channel_url": new_channel_url
    }

    return response