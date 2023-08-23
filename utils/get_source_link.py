import requests

from aiogram.types import BufferedInputFile


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