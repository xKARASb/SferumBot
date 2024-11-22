# Sferum Bot by [@xKARASb](https://github.com/xKARASb)

## Powered by
- [Python 3.11](https://docs.python.org/3.11/)

## Tech
The packages that this application runs on
- [Asyncio]
- [Aiogram 3.x]
- [Requests]

## Features
- Catch text messages and send to TG
- Catch media and send to TG (with TG limits)
- Send forwared messages with media
- You can get messages from several chats

## How to use
#### Install app

- Clone repository:
```sh
git clone https://github.com/xKARASb/SferumBot.git
cd ./SferumBot
```

- Setup eviroment:
```sh
python3 -m venv ./venv
```

- Activate enviroment:
```sh
source ./venv/bin/activate
```
> [!NOTE]
> For Windows use `.\venv\Scripts\Activate`

- Setup dependencies:
```sh
pip install -r requirements.txt
```

#### Setup ```.env``` file

- Authentification cookie for bot:

Go to [Sferum](https://web.vk.me/) >> <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd> >> Application >> Storage >> Cookies >> `https://web.vk.me`
After that you will see a **table** with all cookies from this site!
In filter put `remixdsid` and copy data from `value` column.

_Congratulations 🎉 you get auth cookie now just add it to `AUTH_COOKIE` in `example.env`_

- Bot token:

Go to: [@BotFather](https://t.me/BotFather) and create new bot.
Then put HTTP API token in `BOT_TOKEN` in `example.env`

- Telegram user id:

You can get it from [@username_to_id_bot](https://t.me/username_to_id_bot)
And put your id to `TG_USER_ID` in `example.env`

- Telegram chat id:

If you want the bot to send you messages in private messages, just copy `TG_USER_ID`, else you can create a chat and add the bot there. 
 
> [!IMPORTANT]
> Give administrator rights to your bot

> [!TIP]
> To send messages to one of the topics of supergroup instead of general also add `TG_TOPIC_ID`

- Sferum chat ids:

Get a peer (id) from chat url (`https://web.vk.me/convo/{peer_id}`) and add it to `VK_CHAT_ID`:
```
VK_CHAT_ID="200000015"
VK_CHAT_ID="200000015, 200000016"
```
So you can add several chats

- Rename `example.env` to `.env`

#### Run app
```sh
python startup.py
```

## License 

MIT

**Free Software, Hell Yeah!**

[Asyncio]: <https://docs.python.org/3/library/asyncio.html>
[Aiogram 3.x]: <https://docs.aiogram.dev/en/dev-3.x/index.html>
[Requests]: <https://requests.readthedocs.io/en/latest/>

