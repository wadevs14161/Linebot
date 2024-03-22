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
    TextMessage,
    ImageMessage
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
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    
        return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


@app.route("/find_product", methods=['POST'])
def find_product():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    # try:
    events = parser.parse(body, signature)
    # except InvalidSignatureError:
    #     abort(400)

    for event in events:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            message_input = event.message.text
            if message_input == "1":
                img_url = "https://i.imgur.com/HLw9BhO.jpg"
                reply = ImageMessage(original_content_url=img_url, preview_image_url=img_url)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[reply]))
                break

            result = product_crawl(message_input)
            if result == -1:
                reply1 = "商品不存在日本Uniqlo哦! (期間限定價格商品可能找不到)"
                reply2 = "請重新輸入或按 1 看範例~"
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                    replyToken=event.reply_token, 
                    messages=[TextMessage(text=reply1),
                              TextMessage(text=reply2)]))
            else:
                reply1 = "商品連結\n %s" % result[1]
                reply2 = "商品價格: %d日圓" % result[2]
                reply3 = "折合台幣: %s元" % result[3]
                reply4 = "臺灣官網售價: %s元" % result[4]
                
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                    replyToken=event.reply_token, 
                    messages=[TextMessage(text=reply1),
                              TextMessage(text=reply2),
                              TextMessage(text=reply3),
                              TextMessage(text=reply4)]))
                
    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)