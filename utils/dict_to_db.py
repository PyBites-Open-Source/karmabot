import pickle
from collections import Counter, defaultdict
from pathlib import Path

import slack
from db import db_session
from db.karma_user import KarmaUser

KARMA_CACHE = Path("change_me")


def _load_karma():
    # It is a dict {name (str): points (int)}
    # Name is the slack user "name" attribute usually prefix of the email
    # https://api.slack.com/methods/users.info
    karma_stats: Counter = pickle.load(open(KARMA_CACHE, "rb"))
    return karma_stats


def _get_slack_user_list():
    # https://api.slack.com/methods/users.list
    return slack.SLACK_CLIENT.users_list()["members"]


def _get_available_name(user_info):
    display_name = user_info["profile"]["display_name_normalized"]
    if display_name:
        return display_name

    return user_info["profile"]["real_name_normalized"]


def extract_old_karma():
    old_karma = _load_karma()
    user_list = _get_slack_user_list()

    new_karma = defaultdict(dict)
    for user in user_list:
        name = user["name"]
        if name not in old_karma or user["deleted"]:
            continue

        slack_id = user["id"]
        new_karma[slack_id]["id"] = slack_id
        new_karma[slack_id]["username"] = _get_available_name(user)
        new_karma[slack_id]["karma_points"] = old_karma[name]

    return new_karma


def upload_karma_to_db(new_karma):
    session = db_session.create_session()

    new_users = [
        KarmaUser(
            user_id=user["id"],
            username=user["username"],
            karma_points=user["karma_points"],
        )
        for user in new_karma.values()
    ]

    session.bulk_save_objects(new_users)
    session.commit()
    session.close()


def main():
    db_session.global_init()
    slack.check_connection()

    new_karma = extract_old_karma()
    upload_karma_to_db(new_karma)


if __name__ == "__main__":
    main()
