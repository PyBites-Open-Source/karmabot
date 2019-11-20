import random

import requests

PLATFORM = "https://codechalleng.es"
CC_ES = "CodeChalleng.es"
TIPS_ENDPOINT = "{}/api/tips".format(PLATFORM)
NEW_TIP_LINK = "{}/inbox/new/pytip/".format(PLATFORM)

ADD_TIP = "\nSource: {} | Share more tips: {}\n".format(CC_ES, NEW_TIP_LINK)


def get_random_tip(**kwargs):
    """Print a random Python tip, quote or nugget from CodeChalleng.es"""
    resp = requests.get(TIPS_ENDPOINT)
    tips = resp.json()
    tip = random.choice(tips)
    msg = "> {}\n".format(tip["tip"])
    if tip["link"]:
        msg += "\n{}\n".format(tip["link"])
    if tip["code"]:
        msg += "\n```{}```\n".format(tip["code"])
    msg += ADD_TIP
    return msg


if __name__ == "__main__":
    tip = get_random_tip()
    print(tip)
