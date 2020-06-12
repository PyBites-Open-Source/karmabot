import pickle
from collections import Counter, defaultdict
import os
from pathlib import Path
import sys

from slackclient import SlackClient

token = os.environ.get("SLACK_KARMA_TOKEN")
client = SlackClient(token)

# had to append cwd to PYTHONPATH to get this to work
sys.path.append(os.getcwd())

from bot.db import db_session  # noqa E402
from bot.db.karma_user import KarmaUser  # noqa E402

KARMA_CACHE = Path("change_me")


def _load_karma():
    # It is a dict {name (str): points (int)}
    # Name is the slack user "name" attribute usually prefix of the email
    # https://api.slack.com/methods/users.info
    karma_stats: Counter = pickle.load(open(KARMA_CACHE, "rb"))
    return karma_stats


def _get_slack_user_list():
    # https://api.slack.com/methods/users.list
    members = client.api_call("users.list")["members"]
    print(f"Retrieved {len(members)} members from slack api")
    return members


def _get_available_name(user_info):
    display_name = user_info["profile"]["display_name_normalized"]
    if display_name:
        return display_name

    return user_info["profile"]["real_name_normalized"]


def extract_old_karma():
    old_karma = _load_karma()
    user_list = _get_slack_user_list()

    new_karma = defaultdict(dict)
    print("migrating users ...")

    for user in user_list:
        name = user["name"]
        if name not in old_karma or user["deleted"]:
            continue

        slack_id = user["id"]
        username = _get_available_name(user)
        points = old_karma[name]
        print(f"- {username}: {points}")

        new_karma[slack_id]["id"] = slack_id
        new_karma[slack_id]["username"] = username
        new_karma[slack_id]["karma_points"] = points

    return new_karma


def upload_karma_to_db(new_karma):
    session = db_session.create_session()
    session.execute("""TRUNCATE TABLE karma_user""")
    session.commit()

    new_users = [
        KarmaUser(
            user_id=user["id"],
            username=user["username"],
            karma_points=user["karma_points"],
        )
        for user in new_karma.values()
    ]

    print(f"Inserting {len(new_users)} users in DB")
    session.bulk_save_objects(new_users)
    session.commit()
    session.close()


def main():
    db_session.global_init()

    new_karma = extract_old_karma()
    upload_karma_to_db(new_karma)


if __name__ == "__main__":
    main()
