import sqlalchemy as sa
from bot.db.modelbase import SqlAlchemyBase


class SlackUser(SqlAlchemyBase):
    """ Models a slack user with karma in the DB """

    __tablename__ = "slack_user"

    slack_id = sa.Column(sa.String, primary_key=True)
    username = sa.Column(sa.String)
    karma_points = sa.Column(sa.Integer, default=0)

    def __repr__(self):
        return (
            f"<SlackUser> ID: {self.slack_id} | Username: {self.username} "
            f"| Points:{self.karma_points}"
        )
