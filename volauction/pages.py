from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Auction, Bid
from .forms import BidForm
from utils import cp

########### BLOCK: CONCRETE CLASSES ##############################################################

class GroupCreateWP(WaitPage):
    """
    We form the group of dynamic size based on session.config params (sum of num_traders and num_auctioneers params.

    """
    group_by_arrival_time = True

    def is_displayed(self):
        return self.round_number == 1

    def get_players_for_group(self, waiting_players):
        group_size = self.subsession.group_size
        if len(waiting_players) >= group_size:
            return waiting_players[:group_size]


class Announcement(Page):
    pass


class ChoosingActivity(Page):
    form_model = 'player'
    form_fields = ['auctioneer']

    def before_next_page(self):
        p = self.player
        if p.auctioneer:
            Auction.objects.create(selling_auction=p.role() == Constants.seller,
                                   market=p.group,
                                   auctioneer=p)


class BeforeTradeWP(WaitPage):
    pass


class AuctionPage(Page):
    _allow_custom_attributes = True
    form_model = Bid
    form_fields = ['auction', 'price']
    form_class = BidForm

    def _get_form_model(self):
        return self.form_model

    def get_object(self):
        b, _ = self.form_model.objects.get_or_create(bidder=self.player)
        return b

    def get_form_class(self):
        return self.form_class

    def is_displayed(self):
        return not self.player.auctioneer and self.player.is_auction_available()

    def before_next_page(self):
        self.player.bid_dump = self.player.bid.price


class BeforeResultsWP(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_winning_bids()
        self.group.mark_trader_winners()
        self.group.dump_winning_prices()
        self.group.set_payoffs()


class NoAuction(Page):
    def is_displayed(self):
        if self.player.auctioneer:
            return Auction.objects.filter(auctioneer=self.player, winner__isnull=True).exists()
        else:
            return not self.player.is_auction_available()


class Results(Page):
    pass


page_sequence = [
    GroupCreateWP,
    # Announcement,
    ChoosingActivity,
    BeforeTradeWP,
    AuctionPage,
    BeforeResultsWP,
    NoAuction,
    Results
]
