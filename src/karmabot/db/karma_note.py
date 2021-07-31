import datetime

import sqlalchemy as sa

from karmabot.db.modelbase import SqlAlchemyBase


class KarmaNote(SqlAlchemyBase):
    """Models a simple note system in the DB"""

    __tablename__ = "karma_note"

    id: int = sa.Column(  # noqa
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id = sa.Column(sa.String, sa.ForeignKey("karma_user.user_id"), nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    note = sa.Column(sa.String)

    def __repr__(self):
        return (
            f"[KarmaNote] ID: {self.id} | {self.user_id} -> "
            f"{self.timestamp} | Note: {self.note}"
        )

    def __str__(self):
        return (
            f"(ID: {self.id}) from {self.timestamp.strftime('%Y-%m-%d, %H:%M')}: "
            f"{self.note}."
        )
