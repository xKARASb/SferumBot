import requests

def get_credentials(access_token):
    body = {
        "code": 'var res0 = API.messages.getLongPollHistory({ "lp_version": 19, "credentials": 1, "pts": 10003466, "msgs_limit": 1100, "events_limit": 1100, "last_n": 1000, "extended": 1, "group_id": 0, "fields": "id" });return res0;',
        "access_token": access_token
    }

    req = requests.post("https://api.vk.me/method/execute?v=5.217", data=body)
    return req.json()["response"]["credentials"]

def get_web_token(auth_cookie):
    cookies = {
        "remixdsid": auth_cookie,
    }
    req = requests.post("https://web.vk.me/?act=web_token&app_id=8202606", cookies=cookies)
    return req.json()[1]["access_token"]