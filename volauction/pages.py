from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Auction, Bid
from .forms import BidForm


class Announcement(Page):
    pass


class ChoosingActivity(Page):
    form_model = 'player'
    form_fields = ['auctioneer']

    def before_next_page(self):
        p = self.player
        Auction.objects.create(selling_auction=p.role() == Constants.seller,
                               market=p.group,
                               owner=p)


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
        return not self.player.auctioneer


class Results(Page):
    pass


page_sequence = [
    # Announcement,
    ChoosingActivity,
    AuctionPage,
    # Results
]
