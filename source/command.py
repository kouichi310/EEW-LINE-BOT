from logging import RootLogger, root
import xml.etree.ElementTree as ET
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, FlexSendMessage
)

re_text=""
city_sindo=0
def kuwasiku(root):
    global re_text
    sindo=0
    d_text=""
    for child in root.iter("Earthquake"):
        for child2 in child.iter("Relative"):
            for sindo1 in child2.iter("Group"):
                sindo+=1
                d_text+="\n\n＜震度"+str(sindo1.attrib["Intensity"])+"＞"
                for area in sindo1.iter("Area"):
                    d_text+="\n"+area.attrib["Name"]
    re_text=d_text

def serch_city(root, city_name):
    global city_sindo
    time=""
    shindo=""
    singen=""
    Magnitude=""
    Depth=""
    for child in RootLogger.iter("Earthquake"):
        for child2 in child.iter("Relative"):
            for sindo1 in child2.iter("Group"):
                for area in sindo1.iter("Area"):
                    if(city_name == area.attrib["Name"] or city_name == area.attrib["Name"].replace("市","")):
                        city_sindo=str(sindo1.attrib["Intensity"])

