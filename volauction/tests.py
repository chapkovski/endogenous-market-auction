from otree.api import Currency as c, currency_range, Bot, SubmissionMustFail
from .pages import *

from .models import Constants
import random
from utils import cp


class PlayerBot(Bot):

    def play_round(self):
        yield Announcement,
        act = {'auctioneer': random.choice([True, False])}
        yield ChoosingActivity, act
        if self.player.auctioneer:
            is_a = Auction.objects.filter(auctioneer=self.player, winner__isnull=True).exists()
            if is_a:
                yield NoAuction
        else:
            if self.player.is_auction_available():
                auc = random.choice(self.player.get_available_auctions())
                threshold = auc.auctioneer.evaluation
                if auc.selling:
                    yield SubmissionMustFail(AuctionPage,
                                             {'auction': auc.pk, 'price': random.uniform(0, threshold)})

                    yield AuctionPage, {'auction': auc.pk, 'price': random.uniform(threshold, threshold * 2)}
                else:
                    yield SubmissionMustFail(AuctionPage,
                                             {'auction': auc.pk, 'price': random.uniform(threshold, threshold * 2)})
                    yield AuctionPage, {'auction': auc.pk, 'price': random.uniform(0, threshold)}

            else:
                yield NoAuction
        yield Results
