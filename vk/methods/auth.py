import requests

def get_credentials(access_token):
    body = {
        "code": 'var res0 = API.messages.getLongPollHistory({ "lp_version": 19, "credentials": 1, "pts": 10003466, "msgs_limit": 1100, "events_limit": 1100, "last_n": 1000, "extended": 1, "group_id": 0, "fields": "id" });return res0;',
        "access_token": access_token
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    req = requests.post(
        url = "https://api.vk.me/method/execute?v=5.217",
        data = body,
        headers = headers
    )
    return req.json()["response"]["credentials"]

def get_user_credentials(auth_cookie):
    cookies = {
        "remixdsid": auth_cookie
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    req = requests.get(
        url = "https://web.vk.me/?act=web_token&app_id=8202606",
        cookies = cookies,
        headers = headers,
        allow_redirects = False
    )
    return req.json()[1]