from ast import literal_eval

from aiogram import Bot
from vk.types import Message as VkMessage
from aiogram.types import Message as TgMessage
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaAudio

def text_display(text: str) -> str:
    validate_text = []

    text = "\n".join(text.split("<br>"))

    for char in text:
        if char in ('_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!', ">"):
            validate_text.append("\\")
        validate_text.append(char)
    return "".join(validate_text)

def generate_tg_message(msg: VkMessage) -> tuple[dict, callable]:
    text_entites = []
    commands = []
    if msg.media:
        types = {
        }
        #no pep8
        InputMedia = {
            "photo":InputMediaPhoto,
            "doc": InputMediaDocument,
            "audio": InputMediaAudio
        }
        for attach in msg.media:
            match attach[0]:
                case "video":
                    text_entites.append(f"[Видео {(len(text_entites)+1)}]({attach[1]})")
                case _:
                    types[attach[0]] = types.get(attach[0], [])
                    types[attach[0]].append(InputMedia[attach[0]](media=attach[1], parse_mode="MarkdownV2"))
        types[list(types.keys())[0]][0].caption = text_display(msg.text) + f"\n" + " ".join(text_entites)
        for i in types.keys():
            if len(types[i]) > 1:
                args = {"media": types[i]}
                command = Bot.send_media_group
                commands.append((args, command))
            else:
                command = None
                match types[i][0].type:
                    case "document":
                        command = Bot.send_document
                    case "photo":
                        command = Bot.send_photo
                kwargs = {types[i][0].type: types[i][0].media, "caption": types[i][0].caption, "parse_mode": "MarkdownV2"}
                commands.append((kwargs, command))
        return commands        



    

async def send_message(bot: Bot, msg: VkMessage):
    commands = generate_tg_message(msg)
    for message in commands:
        await message[1](bot, bot.chat_id, **message[0])
    