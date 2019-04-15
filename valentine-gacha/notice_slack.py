import os
import urllib.request
from slackclient import SlackClient


def handler(event, context):
    # チョコあげる人のユーザID
    presenter_id = event["presenter_id"]
    # 当選者のユーザID
    winners_id = event["winners_id"]

    notice_slack(presenter_id, winners_id)


# slack通知
def notice_slack(presenter_id, winners_id):
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