from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService # Similar thing for firefox also!
from subprocess import CREATE_NO_WINDOW

from functions.functions import decrypt_cookie, chek_cookie, get_members
from telegramBot.messages import (
  error_message_cookie_invalid,
  send_photo,
  send_messages
)

import time, json, ast, requests

TIME_UPDATE = 5

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options = webdriver.ChromeOptions()

options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
options.add_argument('--log-level=3')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0")
#options.add_argument('remote-debugging-port=9222')
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")
hrome_service = ChromeService()
hrome_service.creationflags = CREATE_NO_WINDOW


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def fwd_message(profiles, el, tg_id,  text = '') -> str:
  sender = el["from_id"]
  for member in profiles:
    if member["id"] == sender:
      sender = f'{member["first_name"]} {member["last_name"]}'
  text = el["text"] #Последнее пользователя
  message_list = []
  for item in el["fwd_messages"]:
    answer = item["text"] #Комментарий пользователя
    print(answer)
    sender_fwd = item["from_id"]
    for member in profiles:
      if member["id"] == sender_fwd:
        sender_fwd = f'{member["first_name"]} {member["last_name"]}'
    message_list.append((sender_fwd, answer))
    if item.get("fwd_messages", False):
      return fwd_message(profiles, item, message_list)
    elif len(item["attachments"]) > 0:
      media_message(item, tg_id, f"От {sender}\n {' '.join([f' От {x[0]}:                                                                            {x[1]}' for x in message_list])}")
  msg = f"От {sender}\n {' '.join([f' От {x[0]}:                                                                            {x[1]}' for x in message_list])} \n {text}"
  return msg
  


def media_message(el, tg_id, text):
  for attach in el["attachments"]:
    if attach["type"] == "photo": 
      img_url = attach["photo"]["sizes"][len(attach["photo"]["sizes"])-1]["url"]
      send_photo(tg_id, img_url, text)
      return img_url
    
def web_window(cookie, user_id, peer, vk_id):
    cookie = cookie
    tg_id = user_id
    vk_id = vk_id
    peer = peer
    driver = webdriver.Chrome(executable_path="D:\\works\\coding\\python\\sferum\\driver\\chromedriver.exe", options=options, desired_capabilities=caps, service=hrome_service)
    #self.message_handler()
  
    if chek_cookie(cookie).get("error", False):
      print("erroir")
      driver.quit()
      driver.close()
      error_message_cookie_invalid(tg_id)
      return {"error": True}
    #аунтификация
    driver.get("https://web.vk.me")
    driver.add_cookie({"name": "remixdsid", "value": cookie, "domain":"web.vk.me", "path":"/", "secure": True})
    driver.refresh()

    while True:
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
                  if resp["body"]["updates"][0][4] == peer:
                    user_id = resp["body"]["updates"][0][7]["from"]
                    epoch_time = resp["body"]["updates"][0][5]
                    sender = "Unknown"
                    print(resp["body"]["updates"][0][7], type(resp["body"]["updates"][0][7]))
                    print(user_id)
                    for member in get_members(vk_id):
                      print(member)
                      if member["id"] == int(user_id):
                        sender = f'{member["first_name"]} {member["last_name"]}'
                        
                    date = requests.get(f'https://helloacm.com/api/unix-timestamp-converter/?cached&s={epoch_time}').json()
                    msg = resp["body"]["updates"][0][6]
                    print(msg, date)
                    send_messages(tg_id, sender, msg)
          elif el['params']["response"]["url"] == "https://api.vk.me/method/messages.getLongPollHistory?v=5.204":
            resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': el["params"]["requestId"]})
            resp["body"] = json.loads(resp["body"])
            for el in resp["body"]["response"]["messages"]["items"]:
              if el["peer_id"] == peer:
                text = el["text"]
                sender = "Unknown"
                for member in resp["body"]["response"]["profiles"]:
                  print(member)
                  if member["id"] == int(user_id):
                    sender = f'{member["first_name"]} {member["last_name"]}'
                if el.get("fwd_messages", False):
                  text = fwd_message(resp["body"]["response"]["profiles"], el,tg_id,text)
                  send_messages(tg_id, '', text)
                elif el["attachments"]:
                  media_message(el, tg_id, text)
                  