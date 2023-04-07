from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService # Similar thing for firefox also!
from subprocess import CREATE_NO_WINDOW


import time, json, ast, requests
import os
from dotenv import load_dotenv

load_dotenv()

auth_cookie = os.getenv("COOKIE")
bot_token = os.getenv("BOT_TOKEN")

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options = webdriver.ChromeOptions()

options.add_argument('--log-level=3')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0")
#options.add_argument("--headless")
options.add_argument('remote-debugging-port=9222')

chrome_service = ChromeService()
chrome_service.creationflags = CREATE_NO_WINDOW

driver = webdriver.Chrome(executable_path="D:\\works\\coding\\python\\sferum\\driver\\chromedriver.exe", options=options, desired_capabilities=caps, service=chrome_service)


def send_msg(text):
  params = {
     "chat_id": "-1001917922644",
     "text": text,
  }
  requests.get("https://api.telegram.org/bot{bot_token}/sendMessage", params=params)

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


driver.get("https://web.vk.me")

#аунтификация
driver.add_cookie({"name": "remixdsid", "value": auth_cookie, "domain":"web.vk.me", "path":"/", "secure": True})
driver.refresh()

time.sleep(5)

browser_log = driver.get_log('performance')

events = [process_browser_log_entry(entry) for entry in browser_log]

for el in events:
  if el["method"] == "Network.requestWillBeSent":
      if el["params"]["request"]["url"] == "https://api.vk.me/method/account.setOnline?v=5.204":
        auth_token = el["params"]["request"]["postData"].split("=")[1]

        data= {"peer_id": 2000000001, "start_cmid": -1, "count": 10, "offset":0, "extended": 1, "group_id": 0, "fields": "id,first_name,first_name_gen,first_name_acc,last_name,last_name_gen,last_name_acc,sex,has_photo,photo_id,photo_50,photo_100,photo_200,contact_name,occupation,bdate,city,screen_name,online_info,verified,blacklisted,blacklisted_by_me,can_call,can_write_private_message,can_send_friend_request,can_invite_to_chats,friend_status,followers_count,profile_type,contacts,name,type,members_count,member_status,is_closed,can_message,deactivated,activity,ban_info,is_messages_blocked,can_post_donut,site", "access_token":auth_token}
        resp = requests.post("https://api.vk.me/method/messages.getConversationMembers?v=5.204", data=data)

        for i in resp.json()["response"]["profiles"]:
          print(i)

        print()
        
print("while")

while True:
  time.sleep(10)
  browser_log = driver.get_log('performance')
  events = [process_browser_log_entry(entry) for entry in browser_log]
  for el in events:
    if el["method"] == "Network.responseReceived":
      if el['params']["response"]["url"] == "https://api.vk.me/ruim791593813?version=19&mode=682":
        if el["params"].get("requestId", False):
          resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': el["params"]["requestId"]})
          resp["body"] = ast.literal_eval(resp["body"])
          if resp["body"].get("updates", None):
            if len(resp["body"]["updates"][0]) > 5:
              date = requests.get(f'https://helloacm.com/api/unix-timestamp-converter/?cached&s={resp["body"]["updates"][0][5]}').json()
              text = f'{resp["body"]["updates"][0][6]}\n{date}'
              print(text)
              send_msg(text)

