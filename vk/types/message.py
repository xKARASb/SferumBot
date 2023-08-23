from utils import (
    vk_to_tg_poll,
    get_source_link,
    get_max_size_photo
    )

class EventMessage:
    def __init__(self, type, ts, flags, value, chat_id, value2, text, data, attachments, *args, **kwargs) -> None: #i don`t know what is value
        self.__dict__.update(kwargs)
        self.type = type
        self.msg_id = ts
        self.flags = flags
        self.chat_id = chat_id
        self.text = text
        self.sender_id = data.get("from", None)

    def __repr__(self) -> str:
        return f"from {self.sender_id}: {self.text}, media: {' '.join(self.media)}, chat id: {self.chat_id}"


class Message:
    def __init__(self, date, from_id, text, attachments, conversation_message_id, peer_id, **kwargs):
        self.__dict__.update(kwargs)
        self.date = date
        self.sender_id = from_id
        self.text = self.__validate_text(text)
        self.attachments = attachments
        self.chat_msg_id = conversation_message_id
        self.fwd = self.__dict__.get("fwd_messages", None)
        self.chat_id = peer_id
        self.media = []
        self.full_name = self.sender_id
        
        if self.__dict__.get("profiles", False): self.__sender_full_name()
        if self.attachments: self.__parse_attachments()
        if self.fwd: self.__parse_fwds()
        if self.fwd: self.__get_all_media()

    def __parse_attachments(self) -> list:
        media = []
        parsers = {
            "photo": get_max_size_photo,
            "video": lambda x: x["player"],
            "doc": get_source_link,
            "poll": vk_to_tg_poll,
        }
        for attach in self.attachments:
            media_type = attach["type"]
            if media_type in parsers.keys():
                media.append((media_type, parsers[media_type](attach[media_type])))
        self.media = media
        return media
    
    def __parse_fwds(self) -> list:
        fwds = []
        for msg in self.fwd:
            fwds.append(Message(**msg, profiles=self.profiles))
        self.fwd = fwds
        return fwds
    
    def __sender_full_name(self) -> None:
        for profile in self.profiles:
            if profile["id"] == self.sender_id:
                self.first_name = profile["first_name"]
                self.last_name = profile["last_name"]
                self.full_name = f"{self.first_name} {self.last_name}"
        
    def __repr__(self) -> str:
        sender = self.__dict__.get("full_name", self.sender_id)
        string = f" from {sender}: {self.text}, chat id: {self.chat_id}" 
        if self.media:
            string += f", media: {self.media}"
        if self.fwd:
            string += f", fwds: {self.fwd}"
        return string

    def __validate_text(self, text) -> str:
        validate_text = []

        text = "\n".join(text.split("<br>"))

        for char in text:
            if char in ('_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!', ">"):
                validate_text.append("\\")
            validate_text.append(char)
        return "".join(validate_text)    

    def __get_all_media(self) -> list:
        media = []
        if self.fwd:
            for attach in self.fwd: media.extend(Message.__get_all_media(attach))

        for attach in self.media:
            media.append(attach)
        self.media = media
        return media
    
    def get_tg_text(self, fwd_depth = 1) -> str:
        text = f"{self.full_name}:\n{'    '*fwd_depth}{self.text}"
        if self.attachments:
            text += f"\n{'    '*fwd_depth} " + f" ".join([f"*{x[0]}*" if x[0] != "video" else f"[{x[0]}]({x[1]})" for x in self.media ])
        if self.fwd:
            text += f"\n{'    '*fwd_depth}" + f"\n{'    '*fwd_depth}".join([Message.get_tg_text(msg, fwd_depth=fwd_depth+1) for msg in self.fwd])
        return text