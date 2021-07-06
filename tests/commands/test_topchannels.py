# TODO
# def _channel_score(channel):
#     channel_info = channel["channel"]
#     return calc_channel_score(
#         Channel(
#             channel_info["id"],
#             channel_info["name"],
#             channel_info["purpose"]["value"],
#             len(channel_info["members"]),
#             float(channel_info["latest"]["ts"]),
#             channel_info["latest"].get("subtype"),
#         )
#     )


# def test_channel_score(mock_slack_api_call, frozen_now):
#     most_recent = SLACK_CLIENT.api_call("channels.info", channel="CHANNEL42")
#     less_recent = SLACK_CLIENT.api_call("channels.info", channel="CHANNEL43")
#     assert _channel_score(most_recent) > _channel_score(less_recent)


# @patch.dict(os.environ, {"SLACK_KARMA_INVITE_USER_TOKEN": "xoxp-162..."})
# @patch.dict(os.environ, {"SLACK_KARMA_BOTUSER": "U5Z6KGX4L"})
# def test_ignore_message_subtypes(mock_slack_api_call, frozen_now):
#     latest_ignored = SLACK_CLIENT.api_call("channels.info", channel="SOMEJOINS")
#     all_ignored = SLACK_CLIENT.api_call("channels.info", channel="ONLYJOINS")
#     assert _channel_score(latest_ignored) > 0
#     assert _channel_score(all_ignored) == 0
