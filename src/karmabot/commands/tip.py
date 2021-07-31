import random

import requests

PLATFORM = "https://codechalleng.es"
CC_ES = "CodeChalleng.es"
TIPS_ENDPOINT = f"{PLATFORM}/api/tips"
NEW_TIP_LINK = f"{PLATFORM}/inbox/new/pytip/"

ADD_TIP = f"\nSource: {CC_ES} | Share more tips: {NEW_TIP_LINK}\n"


def get_random_tip(**kwargs):
    """Print a random Python tip, quote or nugget from CodeChalleng.es"""
    resp = requests.get(TIPS_ENDPOINT)
    tips = resp.json()
    tip = random.choice(tips)
    msg = f"> {tip['tip']}\n"

    if tip["link"]:
        msg += f"\n{tip['link']}\n"

    if tip["code"]:
        msg += f"\n```{tip['code']}```\n"

    msg += ADD_TIP
    return msg


if __name__ == "__main__":
    tip = get_random_tip()
    print(tip)
