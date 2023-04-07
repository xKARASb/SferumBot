import requests



def get_members(events, user) -> None:
    for el in events:
      if el["method"] == "Network.requestWillBeSent":
          if el["params"]["request"]["url"] == "https://api.vk.me/method/account.setOnline?v=5.204":
            auth_token = el["params"]["request"]["postData"].split("=")[1]

            data= {"peer_id": 2000000001, "start_cmid": -1, "count": 10, "offset":0, "extended": 1, "group_id": 0, "fields": "id,first_name, last_name", "access_token":auth_token}
            resp = requests.post("https://api.vk.me/method/messages.getConversationMembers?v=5.204", data=data)

            for i in resp.json()["response"]["profiles"]:
              print(i)



def encode_cookie(cookie) -> str:
  pass