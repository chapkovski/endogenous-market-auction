from otree.api import Currency as c, currency_range
from .pages import *
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):
        yield Announcement,
        yield ChoosingActivity,
        yield Auction,
        yield Results
