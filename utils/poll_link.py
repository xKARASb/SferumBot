import os
import json
import logging

from aiogram.types import Poll

class LinkedPoll:
    def __init__(self, owner_id: int = None, poll_id: int = None, question: str = None, asnwers: list= None) -> None:
        self.owner_id = owner_id
        self.question = question
        self.poll_id = poll_id
        self.answers = asnwers
        self.linked = False
        
    def add_tg_poll(self, tg_poll: Poll) -> None:
        self.tg_poll_id = tg_poll.id
        answers = []
        for option in tg_poll.options:
            for answer in self.answers:
                if answer["text"] == option.text:
                    answer.update({"tg_id": tg_poll.options.index(option)})
                    answers.append(answer)
        self.answers = answers
        self.linked = True


    def __repr__(self) -> str:
        return f"LinkedPoll {self.poll_id}: {self.question}"

class MessageManager:
    def __init__(self) -> None:
        self.file_name = "linked_msg.json"
        if not os.path.exists(os.path.join(os.getcwd(), self.file_name)):
            data = { "messages": {"polls": {"links": [], "items": []}} }
            self.__write(data)
    
    def __write(self, data, mode = "w") -> None:
        with open(self.file_name, mode) as f:
            json.dump(data, f)
    
    def __get_json(self) -> dict | list:
        with open(self.file_name) as f:
            data = json.load(f)
        return data
    
    def __get_polls(self) -> list:
        return self.__get_json()["messages"]["polls"]
    
    def __write_polls(self, polls) -> None:
        data = self.__get_json()
        data["messages"]["polls"] = polls
        return self.__write(data)
    
    def add_poll(self, vk_poll) -> None:
        polls = self.__get_polls()
        polls["links"].append([vk_poll["id"], ])
        polls["items"].append(LinkedPoll(vk_poll["owner_id"], vk_poll["id"], vk_poll["question"], vk_poll["answers"]).__dict__)
        self.__write_polls(polls)

    def link_poll(self, tg_poll: Poll) -> None:
        polls = self.__get_polls()
        not_linked = polls["links"][len(polls["links"])-1]
        polls["links"].remove(not_linked)
        polls["links"].append([not_linked[0], tg_poll.id])

        for i in reversed(polls["items"]):
            poll = LinkedPoll()
            poll.__dict__ = i
            if not poll.linked:
                polls["items"].remove(poll.__dict__)
                poll.add_tg_poll(tg_poll)
                polls["items"].append(poll.__dict__)
                break
        self.__write_polls(polls)
    
    def get_poll(self, tg_poll_id) -> LinkedPoll | None:
        polls = self.__get_polls()
        for i in polls["links"]:
            if i[1] == tg_poll_id:
                for j in polls["items"]:
                    poll = LinkedPoll()
                    poll.__dict__, j = j, poll
                    if j.poll_id == i[0]:
                        return j
        