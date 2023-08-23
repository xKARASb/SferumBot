class Poll:
    def __init__(self, media, *args, **kwargs) -> None:
        self.__dict__.update(media)
        self.type = "poll"
        self.media = media
        self.tg_poll = media