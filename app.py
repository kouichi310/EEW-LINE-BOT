from flask import Flask, request, abort
from flask import *
import os
import urllib.request
import urllib
import xml.etree.ElementTree as ET
import requests
import json
import pickle
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, FlexSendMessage
)
from source import xml_data, setting, command

app = Flask(__name__)
line_bot_api = LineBotApi(setting.TOKEN)
handler = WebhookHandler(setting.SECRET)
re_text=""
url= 'https://www3.nhk.or.jp/sokuho/jishin/data/JishinReport.xml'

@app.route('/')
def index():
    name = "guest"
    return render_template('index.html',title='siroRabi',name=name)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route('/json', methods=['GET', 'POST', 'DELETE', 'PUT'])
def add():
    jsonData = request.get_json()
    max_inten=0
    if jsonData.get('type') == 'eew':
        magnitude = float(jsonData.get('magnitude'))
        epicenter = str(jsonData.get('epicenter'))
        depth = str(jsonData.get('depth'))
        intensity = str(jsonData.get('intensity'))
        bangou = str(jsonData.get('report'))
        print("max_inten="+str(max_inten)+" now_inten="+intensity)
        if int(intensity) < 3:
            return
        if bangou == "1":
            msg="地　震　速　報　（第"+str(bangou)+"報)\n震　　源　　：　　"+epicenter+"\n予想震度　　：　　"+str(intensity)+"\n規 　　模　　：　　M"+str(magnitude)+"\n深　　さ　　：　　"+str(depth)
            TF=True
            max_inten=str(intensity)
            line_bot_api.broadcast(TextSendMessage(text=msg),notification_disabled=TF)
        if bangou =="final":
            msg="地　震　速　報　（最終報)\n震　　源　　：　　"+str(epicenter)+"\n予想震度　　：　　"+str(intensity)+"\n規　　模　 　：　　M"+str(magnitude)+"\n深　　さ　　：　　"+str(depth)+"\n\n※あくまで予報値です。正確な値はしばらくしてから「最新の地震情報」で取得してください。"
            TF=False
            line_bot_api.broadcast(TextSendMessage(text=msg),notification_disabled=TF)
            max_inten="0"
            return
        if int(intensity) > max_inten:
            msg="地　震　速　報　（第"+str(bangou)+"報)\n震　　源　　：　　"+epicenter+"\n予想震度　　：　　"+str(intensity)+"\n規 　　模　　：　　M"+str(magnitude)+"\n深　　さ　　：　　"+str(depth)
            TF=True
            line_bot_api.broadcast(TextSendMessage(text=msg),notification_disabled=TF)
    if jsonData.get('type') == 'pga_alert_cancel':
        msg = '先ほどの情報は誤報です。'
        line_bot_api.broadcast(TextSendMessage(text=msg))
    return 'OK\n'
    # ... do your business logic, and return some response
    # e.g. below we're just echo-ing back the received JSON data

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    global url,re_text,Line_flex
    xml_data.xml_get(url)
    url_2=""
    for child in xml_data.root:
        url_2=child.find("item").attrib["url"]
        break;
    xml_data.xml_get(url_2)
    xml_data.get_data(xml_data.root)
    if event.message.text == "help":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="＜各種機能の紹介＞\nEEWを受信すると自動で速報を送信します\n\n＜各種コマンドの紹介＞\n・最新の地震情報\n直近の地震情報をの概要を表示してくれます\n\n"
            "・最新の地震情報を詳しく\n直近の地震情報を詳しく表示してくれます\n\n"
            "・市町村検索 <市町村名>\n指定した市町村が最近の地震情報にあるかを確かめ震度を表示してくれます。")
        )
    if event.message.text == "最新の地震情報":
        #message_and_image = json.dumps(message_and_image)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=xml_data.re_text)
        )
        if(event.source.type == "group"):
            line_bot_api.push_message(
                event.source.group_id,
                ImageSendMessage(original_content_url=xml_data.image_url_big,preview_image_url=xml_data.image_url_big)
            )
        else:
            line_bot_api.push_message(
                event.source.user_id,
                ImageSendMessage(original_content_url=xml_data.image_url_big,preview_image_url=xml_data.image_url_big)
            )
    if event.message.text == "最新の地震情報を詳しく":
        command.kuwasiku(xml_data.root)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="最新の地震情報をより詳細にお伝えします\n"+xml_data.re_text.replace("最新の地震情報をお伝えします","")+command.re_text)
        )
        if(event.source.type == "group"):
            line_bot_api.push_message(
                event.source.group_id,
                ImageSendMessage(original_content_url=xml_data.image_url_small,preview_image_url=xml_data.image_url_small)
            )
        else:
            line_bot_api.push_message(
                event.source.user_id,
                ImageSendMessage(original_content_url=xml_data.image_url_small,preview_image_url=xml_data.image_url_small)
            )
    if "市町村検索" in event.message.text:
        command.serch_city(xml_data.root, event.message.text.replace("市町村検索 ",""))
        if command.city_sindo==0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="最新の地震情報には"+event.message.text.replace("市町村検索 ","")+"はありませんでした。")
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text.replace("市町村検索 ","")+"は震度"+command.city_sindo+"でした。")
            )
            command.city_sindo=0
            if(event.source.type == "group"):
                line_bot_api.push_message(
                    event.source.group_id,
                    ImageSendMessage(original_content_url=xml_data.image_url_small,preview_image_url=xml_data.image_url_small)
                )
            else:
                line_bot_api.push_message(
                    event.source.user_id,
                    ImageSendMessage(original_content_url=xml_data.image_url_small,preview_image_url=xml_data.image_url_small)
                )



if __name__ == "__main__":
    app.run()