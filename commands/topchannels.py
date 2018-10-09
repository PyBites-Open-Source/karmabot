TOP_CHANNELS = """Glad you asked, here are some channels our Communtiy recommends:
- #100daysofcode: share your 100 days journey and/or feedback on our course
- #books: get notified about Packt's daily free ebook and/or share interesting books you are reading
- #codechallenges: stuck? Ask your Python coding questions here, we learn more together!
- #instagram: submit inspiring Python/coding/developer pictures for PyBites Instagram
- #meetups / #pycon: the PyBites community is growing so maybe you can meet fellow Pythonistas in person!
- #pybites-news: share interesting Python news/articles here helping us with our weekly Twitter news digest
- #checkins: share your pythonic adventures with the community and help everyone grow!
"""


def get_recommended_channels(**kwargs):
    """Show some of our Community's favorite channels you can join"""
    return TOP_CHANNELS


if __name__ == '__main__':
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = get_recommended_channels(**kwargs)
    print(output)
