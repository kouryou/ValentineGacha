import os
import urllib.request
from slackclient import SlackClient


def handler(event, context):
    """ハンドラ関数

    Parameters
    ----------
    event : dict
        イベントデータ
    context : dict
        ランタイム情報
    """
    # チョコあげる人のユーザID
    presenter_id = event["presenter_id"]
    # 当選者のユーザID
    winners_id = event["winners_id"]

    # slack通知
    notice_slack(presenter_id, winners_id)


def notice_slack(presenter_id, winners_id):
    """slack通知

    Parameters
    ----------
    presenter_id : str
        チョコあげる人のユーザID
    winners_id : str
        当選者のユーザID
    """
    # 当選者のメンション一覧を作成
    winners_mention = "".join(["<@" + winner_id + ">さん\n"
                               for winner_id in winners_id])

    # 通知用メッセージ組み立て
    send_text = "<@" + presenter_id + ">です :heart: \n" + winners_mention \
              + "よかったらチョコ受けとってくれると嬉しいな :two_hearts:"

    # メッセージ画像取得
    image = urllib.request.urlopen(os.environ["MESSAGE_IMAGE_URL"]).read()

    # SlackClient作成
    sc_bot = SlackClient(os.environ["SLACK_BOT_TOKEN"])

    # slack通知
    sc_bot.api_call(
        "files.upload",
        initial_comment=send_text,
        file=image,
        channels=os.environ["SLACK_NOTICE_CHANNEL"]
    )