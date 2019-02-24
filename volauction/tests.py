from otree.api import Currency as c, currency_range
from .pages import *
from ._builtin import Bot
from .models import Constants
import random
from utils import cp

class PlayerBot(Bot):

    def play_round(self):
        # yield Announcement,
        act = {'auctioneer': True if self.player.role() == Constants.seller else False}
        yield ChoosingActivity, act
        if not self.player.auctioneer:
            # todo: select only auctions of correct type
            auc = random.choice(self.group.get_available_auctions())
            yield AuctionPage, {'auction': auc.pk, 'price': random.randint(0, 100)}
        yield Results
