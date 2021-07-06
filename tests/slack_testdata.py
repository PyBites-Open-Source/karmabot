from karmabot.settings import KARMABOT_ID

TEST_USERINFO = {
    "ABC123": {
        "ok": True,
        "user": {
            "id": "ABC123",
            "team_id": "TKRQZ0DN3",
            "name": "bob",
            "deleted": False,
            "real_name": "Bob Belderbos",
            "profile": {
                "real_name": "Bob Belderbos",
                "real_name_normalized": "Bob Belderbos",
                "display_name": "pybob",
                "display_name_normalized": "pybob",
            },
        },
    },
    "EFG123": {
        "ok": True,
        "user": {
            "id": "EFG123",
            "team_id": "TKRQZ0DN3",
            "name": "julian",
            "deleted": False,
            "real_name": "Julian Sequeira",
            "profile": {
                "real_name": "Julian Sequeira",
                "real_name_normalized": "Julian Sequeira",
                "display_name": "",
                "display_name_normalized": "",
            },
        },
    },
    "XYZ123": {
        "ok": True,
        "user": {
            "id": "XYZ123",
            "team_id": "TKRQZ0DN3",
            "name": "",
            "deleted": False,
            "real_name": "Martin Uribe",
            "profile": {
                "real_name": "Martin Uribe",
                "real_name_normalized": "Martin Uribe",
                "display_name": "clamytoe",
                "display_name_normalized": "clamytoe",
            },
        },
    },
}


TEST_EVENT_MSG = {
    "channel_simple": [
        {
            "client_msg_id": "123e4dd-88bb-1234-aa12-8fbf66c1234a",
            "suppress_notification": False,
            "type": "message",
            "text": "Test message 123",
            "user": "ABC123",
            "team": "TKRQZ0DN3",
            "user_team": "TKRQZ0DN3",
            "source_team": "TKRQZ0DN3",
            "channel": "GP5TCC5V1",
            "event_ts": "1571TKRQZ0DN3",
            "ts": "1571341892.003000",
        }
    ],
    "channel_karma": [],
    "channel_command": [],
}

# TODO
TEST_EVENT_TEAMJOIN = [{"type": "team_join"}]

TEST_CHANNEL_INFO = {
    "CHANNEL42": {
        "ok": True,
        "channel": {
            "id": "CHANNEL42",
            "name": "Awesome Test Channel",
            "is_channel": True,
            "created": 1466025154,
            "creator": "ABC123",
            "name_normalized": "Awesome Test Channel",
            "last_read": "1503435939.000101",
            "latest": {
                "text": "Containment unit is 98% full",
                "username": "karmabot",
                "bot_id": KARMABOT_ID,
                "attachments": [
                    {
                        "text": "Don't get too attached",
                        "id": 1,
                        "fallback": "This is an attachment fallback",
                    }
                ],
                "type": "message",
                "subtype": "bot_message",
                "ts": "1503435956.000247",
            },
            "unread_count": 1,
            "unread_count_display": 1,
            "members": ["ABC123", "EFG123"],
            "topic": {
                "value": "Spiritual containment strategies",
                "creator": "ABC123",
                "last_set": 1503435128,
            },
            "purpose": {
                "value": "Discuss busting ghosts",
                "creator": "ABC123",
                "last_set": 1503435128,
            },
            "previous_names": ["dusting"],
        },
    },
    "CHANNEL43": {
        "ok": True,
        "channel": {
            "id": "CHANNEL43",
            "name": "Slightly Less Awesome Test Channel",
            "is_channel": True,
            "created": 1466025154,
            "creator": "ABC123",
            "name_normalized": "Slightly Less Awesome Test Channel",
            "last_read": "1503435939.000101",
            "latest": {
                "text": "Hamsters are small but fast",
                "username": "karmabot",
                "bot_id": KARMABOT_ID,
                "attachments": [],
                "type": "message",
                "subtype": "bot_message",
                "ts": "1503353156.000247",
            },
            "unread_count": 1,
            "unread_count_display": 1,
            "members": ["ABC123", "EFG123"],
            "topic": {
                "value": "Having less active discussions",
                "creator": "ABC123",
                "last_set": 1503435128,
            },
            "purpose": {
                "value": "Do things and talk about stuff",
                "creator": "ABC123",
                "last_set": 1503435128,
            },
            "previous_names": ["pancakes"],
        },
    },
    "SOMEJOINS": {
        "ok": True,
        "channel": {
            "id": "SOMEJOINS",
            "name": "Some joiny bits with a dash of chatter",
            "is_channel": True,
            "created": 1466025154,
            "creator": "ABC123",
            "name_normalized": "Some joiny bits with a dash of chatter",
            "last_read": "1503435939.000101",
            "latest": {
                "type": "message",
                "subtype": "channel_join",
                "ts": "1503353156.000247",
                "user": "URVU20YHL",
                "text": "<@URVU20YHL> has joined the channel",
            },
            "members": ["ABC123", "EFG123"],
            "purpose": {
                "value": "Drink milk loudly through a straw",
                "creator": "ABC123",
                "last_set": 1503435128,
            },
        },
    },
    "ONLYJOINS": {
        "ok": True,
        "channel": {
            "id": "ONLYJOINS",
            "name": "Nothing but join messages in here",
            "is_channel": True,
            "created": 1466025154,
            "creator": "ABC123",
            "name_normalized": "Nothing but join messages in here",
            "last_read": "1503435939.000101",
            "latest": {
                "type": "message",
                "subtype": "channel_join",
                "ts": "1503353156.000247",
                "user": "URVU20YHL",
                "text": "<@URVU20YHL> has joined the channel",
            },
            "members": ["ABC123", "EFG123"],
            "purpose": {
                "value": "Watch people walk through the door",
                "creator": "ABC123",
                "last_set": 1503435128,
            },
        },
    },
}

TEST_CHANNEL_HISTORY = {
    "SOMEJOINS": {
        "ok": True,
        "messages": [
            {
                "type": "message",
                "subtype": "channel_join",
                "ts": "1503353156.000247",
                "user": "URW2VDFK6",
                "text": "<@URW2VDFK6> has joined the channel",
                "inviter": "URVU20YHL",
            },
            {
                "client_msg_id": "4858ae10-a803-4e01-80ff-28eb23776a60",
                "type": "message",
                "text": "test",
                "user": "URVU20YHL",
                "ts": "1503353087.000247",
                "team": "TRTMY06HW",
                "blocks": [
                    {
                        "type": "rich_text",
                        "block_id": "gqY",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [{"type": "text", "text": "test"}],
                            }
                        ],
                    }
                ],
            },
        ],
        "has_more": False,
        "channel_actions_ts": None,
        "channel_actions_count": 0,
    },
    "ONLYJOINS": {
        "ok": True,
        "messages": [
            {
                "type": "message",
                "subtype": "channel_join",
                "ts": "1503353156.000247",
                "user": "URW2VDFK6",
                "text": "<@URW2VDFK6> has joined the channel",
                "inviter": "URVU20YHL",
            },
            {
                "type": "message",
                "subtype": "channel_join",
                "ts": "1503353087.000247",
                "user": "URVU20YHL",
                "text": "<@URVU20YHL> has joined the channel",
            },
        ],
        "has_more": False,
        "channel_actions_ts": None,
        "channel_actions_count": 0,
    },
}
