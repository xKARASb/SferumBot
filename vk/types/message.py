import requests
from aiogram.types import BufferedInputFile

def get_max_size_photo_url(attach) -> str: 
    link = (0, 100)
    lvls = ("w", "z", "y", "r", "q", "p", "o", "x", "m", "s")

    for i in attach["sizes"]:
      if lvls.index(i["type"]) < link[1]:
         link = (i["url"], lvls.index(i["type"]))
    return link[0]

def get_source_link(attach) -> str:
    req = requests.get(attach["url"])
    if "text" in req.headers.get("Content-Type").split("/"): 
        url = req.text[req.text.find("https:", req.text.find("docUrl")):req.text.find('",', req.text.find("docUrl"))]
        req = requests.get(''.join(url.split("\\")))
        if len(req.content) < 52428800: 
            return BufferedInputFile(req.content, filename=req.url[req.url.rfind("/")+1:req.url.find("?")])
    elif "application" in req.headers.get("Content-Type").split("/"):
        return BufferedInputFile(req.content, filename=req.url[req.url.rfind("/")+1:req.url.find("?")])
    else: 
        return attach["url"]

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
        self.text = text
        self.attachments = attachments
        self.chat_msg_id = conversation_message_id
        self.fwd = self.__dict__.get("fwd_messages", None)
        self.chat_id = peer_id
        self.media = []
        self.full_name = self.sender_id
        
        if self.__dict__.get("profiles", False): self.__sender_full_name()
        if self.attachments: self.__parse_attachments()
        if self.fwd: self.__parse_fwds()

    def __parse_attachments(self) -> list:
        media = []
        parsers = {
            "photo": get_max_size_photo_url,
            "video": lambda x: x["player"],
            "doc": get_source_link,
        }
        for attach in self.attachments:
            media_type = attach["type"]
            if media_type in parsers.keys():
                media.append((media_type, parsers[media_type](attach[media_type])))
        self.media = media
        print(media)
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
