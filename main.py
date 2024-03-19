from flask import Flask, jsonify, request, abort
import os
import sys
from argparse import ArgumentParser

from linebot import (
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from crawl import product_crawl

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

parser = WebhookParser(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        '''
        Looks like the 4 line code below makes railway app crash
        '''
        # if not isinstance(event, MessageEvent):
        #     continue
        # if not isinstance(event.message, TextMessageContent):
        #     continue
        # text=event.message.text
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )

    return 'OK'

@app.route("/find_product", methods=['POST'])
def find_product():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        message_input = event.message.text
        result = product_crawl(message_input)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            if result == -1:
                reply = "商品不存在日本Uniqlo哦!"
                line_bot_api.reply_message(ReplyMessageRequest(
                        replyToken=event.reply_token, 
                        messages=[TextMessage(text=reply)])
                )
            else:
                reply1 = "商品連結\n %s" % result[1]
                reply2 = "商品價格: %d日圓" % result[2]
                line_bot_api.reply_message(ReplyMessageRequest(
                        replyToken=event.reply_token, 
                        messages=[TextMessage(text=reply1), TextMessage(text=reply2)])
                )

    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)