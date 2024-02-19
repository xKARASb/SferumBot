def vk_to_tg_poll(vk_poll) -> dict:
    kwargs = {
        "question": vk_poll["question"],
        "options": [x["text"] for x in vk_poll["answers"]],
        "is_anonymous": vk_poll["anonymous"],
        "allows_multiple_answers": vk_poll["multiple"]
    }
    if vk_poll["end_date"]: kwargs.update({"close_date": vk_poll["end_date"]})
    return kwargs