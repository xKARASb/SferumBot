def get_max_size_photo_url(attach) -> str: 
    link = (0, 100)
    lvls = ("w", "z", "y", "r", "q", "p", "o", "x", "m", "s")

    for i in attach["sizes"]:
      if lvls.index(i["type"]) < link[1]:
         link = (i["url"], lvls.index(i["type"]))
    return link[0]
