import logging

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

from functions.functions import decrypt_cookie, chek_cookie, get_members
from telegramBot.messages import (
  error_message_cookie_invalid,
  send_media,
  send_messages,
  send_photo,
  send_doc
)


import time, json, ast, requests, logging, os, signal, sys

driver_path = os.getenv('PATH')

logger = logging.getLogger('urllib3.connectionpool')
logger.setLevel(logging.INFO)

logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.INFO)

TIME_UPDATE = 5

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options = webdriver.ChromeOptions()

options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
options.add_argument('--log-level=3')
#options.add_argument("disable-logging")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
hrome_service = ChromeService()

class GracefulKiller:
  kill_now = False
  def __init__(self, tg_id):
    self.tg_id = tg_id
    signal.signal(signal.SIGINT, self.exit_int)
    signal.signal(signal.SIGTERM, self.exit_term)

  def exit_int(self, *args):
    self.kill_now = True
    send_messages(self.tg_id, "Системное оповещение", "Обработчик сферума пошёл спать по плану((")
    with open("autoconnect/active_pool.json", "r") as f:
      data = json.load(f)
    data.pop(str(self.tg_id))
    with open("autoconnect/active_pool.json", "w") as f:
      json.dump(data, f)

  def exit_term(self, *args):
    send_messages(self.tg_id, "Системное оповещение", "Обработчик сферума пошёл спать((")
    self.kill_now = True
    print("Killing...")
    with open("autoconnect/active_pool.json", "r") as f:
      data = json.load(f)
    data.pop(str(self.tg_id))
    with open("autoconnect/active_pool.json", "w") as f:
      json.dump(data, f)

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

#обработка пересланных сообщений
def fwd_message(profiles, el, text = None, count = 0):
  count += 1
  all_messages = [] if text is None else text
  media = [[],[]]
  for i in el["fwd_messages"]:
    text = i.get("text")
    user_id = i.get("from_id")

    #Опеределение отправителя
    for user in profiles:
      if user_id == user["id"]:
        sender = f'От {user["first_name"]} {user["last_name"]}:'
    fwd_messages = ""
    if len(i.get("attachments")) > 0:
      raw_media = media_message(i)
      if raw_media[0]:
        media[0] += raw_media[0]
        for attachment in raw_media[0]:
          match attachment[0]:
            case "doc":
              text = f'{text} *документ*'
            case "photo":
              text = f'{text} *фото*'
      if raw_media[1]:
        media[1] += raw_media[1]
        for k in range(len(raw_media[1])):
          text = f'{text} *видео*'

    if i.get("fwd_messages", False):
      raw_data = fwd_message(profiles, i, count=count)
      raw_media = raw_data[1]
      media[0] += raw_media[0]
      media[1]+= raw_media[1]
      fwd_messages = raw_data[0]
    msg = f"{'  '*count}{sender}\n  {''.join(fwd_messages)}"
    if text:
      msg = f"{' '*count}{sender}\n  {'  '*(count+1)}{''.join(text)}\n  {''.join(fwd_messages)} "

    all_messages.append(msg)
    
  return all_messages, media
  
    
#Обработка медиа
def media_message(el):
  urls = []
  videos = []
  for attach in el["attachments"]:
    match attach["type"]:
      case "photo":
        media_url = attach["photo"]["sizes"][len(attach["photo"]["sizes"])-1]["url"]
        urls.append((attach["type"], media_url))
      case "video":
        media_url = attach["video"]["player"]
        videos.append(f'({media_url})')
      case "doc":
        media_url = attach["doc"]["url"]
        media_title = attach["doc"]["title"]
        print(media_url)
        urls.append((attach["type"], media_url, media_title))

  return urls, videos
    
def web_window(cookie, user_id, peer, vk_id, handl = None):
  cookie = cookie
  tg_id = user_id
  vk_id = vk_id
  peer = peer

  killer = handl if handl else GracefulKiller(tg_id)

  try:   
    driver = webdriver.Chrome(executable_path=driver_path, options=options, desired_capabilities=caps, service=hrome_service)
    #self.message_handler()

    if chek_cookie(cookie).get("error", False):
      logging.warning(f"Bad cookie\n User: {tg_id}")
      driver.quit()
      driver.close()
      error_message_cookie_invalid(tg_id)
      return {"error": True}
    #аунтификация
    driver.get("https://web.vk.me")
    driver.add_cookie({"name": "remixdsid", "value": cookie, "domain":"web.vk.me", "path":"/", "secure": True})
    driver.add_cookie({"name": "remixweb_vk_me_profile_type", "value":"2", "domain":"web.vk.me"})
    driver.refresh()

    send_messages(tg_id, "Системное оповещение", "Бот подключён!")
      #основной поток обработки сообщений сферума
    while not killer.kill_now:
      time.sleep(TIME_UPDATE)
      browser_log = driver.get_log('performance')
      events = [process_browser_log_entry(entry) for entry in browser_log]
      for el in events:
        if el["method"] == "Network.responseReceived":
          if el['params']["response"]["url"] == f"https://api.vk.me/ruim{vk_id}?version=19&mode=682":
            if el["params"].get("requestId", False):
              resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': el["params"]["requestId"]})
              resp["body"] = ast.literal_eval(resp["body"])
              if resp["body"].get("updates", None):
                if len(resp["body"]["updates"][0]) > 5:
                  if not resp["body"]["updates"][0][8]:
                    if resp["body"]["updates"][0][4] == peer:
                      user_id = resp["body"]["updates"][0][7]["from"]
                      sender = "Unknown"
                      for member in get_members(vk_id):
                        if member["id"] == int(user_id):
                          sender = f'{member["first_name"]} {member["last_name"]}'
                      msg = resp["body"]["updates"][0][6]
                      logging.info(f"NEW MESSAGE\n {sender}:{msg}")
                      send_messages(tg_id, sender, msg)
          # Обработка медиа и файлов
          elif el['params']["response"]["url"] == "https://api.vk.me/method/messages.getLongPollHistory?v=5.204":
            resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': el["params"]["requestId"]})
            resp["body"] = json.loads(resp["body"])
            for el in resp["body"]["response"]["messages"]["items"]:
              logging.warning(f"RESP \n{resp}")
              if el["peer_id"] == peer:
                text = el["text"]
                user_id = el["from_id"]
                for member in resp["body"]["response"]["profiles"]:
                  if member["id"] == int(user_id):
                    sender = f'{member["first_name"]} {member["last_name"]}'
                if el.get("fwd_messages", False):
                  text_fwd = fwd_message(resp["body"]["response"]["profiles"], el)
                  message = f" {text} \n {''.join(text_fwd[0])}"
                  video = None
                  if text_fwd[1][1]:
                    video = f"[Видео]{' [Видео]'.join(text_fwd[1][1])}"
                  send_messages(tg_id, sender, message, video)
                  if text_fwd[1][0]:
                    if len(text_fwd[1][0]) > 1:
                      send_media(tg_id, text_fwd[1][0])
                    else:
                      send_photo(tg_id, sender, text_fwd[1][0][0][1])
                elif el["attachments"]:
                  urls = media_message(el)
                  video = None  
                  if urls[1]:
                    video = f"[Видео]{' [Видео]'.join(urls[1])}"
                  send_messages(tg_id, sender, text, video)
                  if urls[0]:
                    if len(urls[0]) > 1:
                      send_media(tg_id, urls[0])
                    else:
                      match urls[0][0][0]:
                        case 'photo':
                          send_photo(tg_id, sender, urls[0][0][1])
                        case "doc":
                          send_doc(tg_id, urls[0][0][2], urls[0][0][1])
    
    logging.info(f"Browser shootdown \n user id:{tg_id}")
    driver.quit()

    #sys.exit(1)
  except Exception as e:
    if not killer.kill_now:
      driver.quit()
      logging.error("Browser error")
      logging.exception("error")

      web_window(cookie, tg_id, peer, vk_id)
    else:
      logging.info(f"Browser shootdown \n user id:{tg_id}")
      driver.quit()

      #sys.exit(1)