from aiogram import Bot
from vk.types import Message as VkMessage
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaAudio, Message


def generate_tg_message(msg: VkMessage) -> tuple[dict, callable]:
    text = f"·{msg.chat_title}·\n{msg.get_tg_text()}"
    media = msg.media
    commands = []

    if media:
        types = {}

        #no pep8
        InputMedia = {
            "photo":InputMediaPhoto,
            "doc": InputMediaDocument,
            "audio": InputMediaAudio,
        }

        for attach in media:
            if attach[0] == "video":
                continue
            types[attach[0]] = types.get(attach[0], [])
            types[attach[0]].append(InputMedia[attach[0]](media=attach[1],
                                                            parse_mode="MarkdownV2"))
        
        types[list(types.keys())[0]][0].caption = text
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

                kwargs = {
                    types[i][0].type: types[i][0].media,
                    "caption": types[i][0].caption,
                    "parse_mode": "MarkdownV2"
                    }
                commands.append((kwargs, command))  
    else:
        commands.append(({"text": text, "parse_mode": "MarkdownV2"}, Bot.send_message))
    return commands

async def send_message(bot: Bot, msg: VkMessage, tg_chat_id: int):
    commands = generate_tg_message(msg)
    for message in commands:
        message: Message = await message[1](bot, tg_chat_id, **message[0])