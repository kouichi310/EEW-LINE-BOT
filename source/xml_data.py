import urllib.request
import urllib
import xml.etree.ElementTree as ET
import requests
#NHKより地震のXMLファイルをスクレイピングする関数
root=""
re_text=""
image_url_big=""
image_url_small=""
image_url_nomal=""

def xml_get(url):
    global root
    headers1 = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
        }
    req = urllib.request.Request(url, headers=headers1)
    with urllib.request.urlopen(req) as response:
        XmlData = response.read()
        XmlData = XmlData.decode("Shift-JIS")
        root=ET.fromstring(XmlData)
        tree = ET.ElementTree(root)
        tree.write("zishin.xml")
#そのＸＭＬファイルから必要なデータを抜き出す関数
def get_data(root):
    global re_text,image_url_big,image_url_small
    time=""
    shindo=""
    singen=""
    Magnitude=""
    Depth=""
    image_url_big=""
    image_url_nomal=""
    image_url_small = ""
    for child in root.iter("Earthquake"):
        time=child.attrib["Time"]
        shindo=child.attrib["Intensity"]
        singen=child.attrib["Epicenter"]
        Magnitude=child.attrib["Magnitude"]
        Depth=child.attrib["Depth"]
        image_url_big="https://www3.nhk.or.jp/sokuho/jishin/"+child.find("Detail").text
        image_url_nomal="https://www3.nhk.or.jp/sokuho/jishin/"+child.find("Local").text
        image_url_small="https://www3.nhk.or.jp/sokuho/jishin/"+child.find("Global").text
        re_text = "最新の地震情報をお伝えします\n発生時間："+time+"\n震源："+singen+"\nマグニチュード："+Magnitude+        "\n深さ ："+Depth+"\n最大震度："+shindo