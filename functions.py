import requests, os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

key = (os.getenv("KEY")).encode("utf-8")

def get_members(events, user) -> None:
    for el in events:
      if el["method"] == "Network.requestWillBeSent":
          if el["params"]["request"]["url"] == "https://api.vk.me/method/account.setOnline?v=5.204":
            auth_token = el["params"]["request"]["postData"].split("=")[1]

            data= {"peer_id": 2000000001, "start_cmid": -1, "count": 10, "offset":0, "extended": 1, "group_id": 0, "fields": "id,first_name, last_name", "access_token":auth_token}
            resp = requests.post("https://api.vk.me/method/messages.getConversationMembers?v=5.204", data=data)

            for i in resp.json()["response"]["profiles"]:
              print(i)



def encrypt_cookie(cookie: str) -> str:
  fernet = Fernet(key)
  encrypted = fernet.encrypt(cookie.encode()).decode()
  return encrypted

def decrypt_cookie(encryp_cookie: str) -> str:
  fernet = Fernet(key)
  dectex = fernet.decrypt(encryp_cookie.encode()).decode()
  return dectex