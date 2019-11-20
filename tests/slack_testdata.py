from bot.settings import KARMABOT_ID

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
                "real_name_normalized": "Patrick",
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
    }
}
