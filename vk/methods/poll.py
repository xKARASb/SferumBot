import requests

from aiogram.types import PollAnswer
from utils import MessageManager

def send_vote(tg_poll: PollAnswer, access_token):
    poll = MessageManager().get_poll(tg_poll.poll_id)
    vote_answers = [str(x["id"]) for x in poll.answers if x["tg_id"] in tg_poll.option_ids]
    data = {
        "owner_id": poll.owner_id,
        "poll_id": poll.poll_id
    }
    body = {
        "access_token": access_token,
        "code": f"var res0=API.polls.deleteVote({data}); return res0;"
    }
    if vote_answers:
        data.update({"answer_ids": ",".join(vote_answers)})
        body["code"] = f'var res0 = API.polls.addVote({data}); return res0;'
    requests.post(
        url = "https://api.vk.me/method/execute?v=5.217",
        data = body
    )