from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期

city = '重庆'
birthday = '12-31'

app_id = 'wx3d3287c20f6f470a'
app_secret = '0939e4b6ca248c4e0d28f36679ca379a'

user_id = 'o_TZC52g07dw3FfSmS1YSulE9T0o'
template_id = 'GdSa_WuN_5F2faqKH3VOec-r117l5KamiG0Y1DqLhfY'

if app_id is None or app_secret is None:
  print('请设置 APP_ID 和 APP_SECRET')
  exit(422)

if not user_id:
  print('请设置 USER_ID，若存在多个 ID 用回车分开')
  exit(422)

if template_id is None:
  print('请设置 TEMPLATE_ID')
  exit(422)

# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather():
  if city is None:
    print('请设置城市')
    return None
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  if res is None:
    return None
  weather = res['data']['list'][0]
  return weather

# 获取当前日期为星期几
def get_week_day():
  week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  week_day = week_list[datetime.date(today).weekday()]
  return week_day


# 生日倒计时
def get_birthday_left():
  if birthday is None:
    print('没有设置 BIRTHDAY')
    return 0
  next = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
  if next < nowtime:
    next = next.replace(year=next.year + 1)
  return (next - today).days

# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功
def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def format_temperature(temperature):
  return math.floor(temperature)

# 随机颜色
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
weather = get_weather()
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "city": {
    "value": city,
    "color": get_random_color()
  },
  "date": {
    "value": today.strftime('%Y年%m月%d日'),
    "color": get_random_color()
  },
  "week_day": {
    "value": get_week_day(),
    "color": get_random_color()
  },
  "weather": {
    "value": weather['weather'],
    "color": get_random_color()
  },
  "humidity": {
    "value": weather['humidity'],
    "color": get_random_color()
  },
  "wind": {
    "value": weather['wind'],
    "color": get_random_color()
  },
  "air_data": {
    "value": weather['airData'],
    "color": get_random_color()
  },
  "air_quality": {
    "value": weather['airQuality'],
    "color": get_random_color()
  },
  "temperature": {
    "value": math.floor(weather['temp']),
    "color": get_random_color()
  },
  "highest": {
    "value": math.floor(weather['high']),
    "color": get_random_color()
  },
  "lowest": {
    "value": math.floor(weather['low']),
    "color": get_random_color()
  },

  "birthday_left": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "words": {
    "value": get_words(),
    "color": get_random_color()
  },
}

if __name__ == '__main__':
  try:
     res = wm.send_template(user_id, template_id, data)

  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了消息")
