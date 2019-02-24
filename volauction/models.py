"""
Data storage and logic for endogeous market formation game.

"""
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
from django.db.models import Max, Min
import random
from utils import cp

author = 'Philipp Chapkovski, chapkovski@gmail.com HSE-Moscow'

doc = """
Endogenuous market formation. 

"""

# TODO: check for conflicts (no auctions to participate in)
"""
There are two types of conflicts possible.
1. A person chooses to be an auctioneer, but no one chooses his auction. (it also includes the case when everyone
from the opposing type chooses to be an auctioneer.

2. A person decides to be a trader, but there are no auctions to attend.
"""

########### BLOCK: ERROR MESSAGES ##############################################################
SELLERS_ERR_MSG = 'Number of sellers per group should be less than total number of market participants'


############ END OF: ERROR MESSAGES #############################################################


class Constants(BaseConstants):
    name_in_url = 'volauction'
    # todo: make group size adjustable (see speed_app)
    players_per_group = 3
    num_rounds = 1
    num_sellers = 1
    assert num_sellers < players_per_group, SELLERS_ERR_MSG
    buyer, seller = 'Buyer', 'Seller'  # keep role names here so we can change them later in one spot
    AUCTIONEER_CHOICES = [(True, 'Auctioneer'), (False, 'Participant in someone\'s auction')]
    lb, ub = 0, 10  # lower and upper boundaries of evaluation
    earning_if_none = 0  # Earnings of traders and auctioneers if no auction is won or happened


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.evaluation = random.uniform(Constants.lb, Constants.ub)
            p.direction = 1 if p.role() == Constants.seller else -1


class Group(BaseGroup):
    def set_payoffs(self):
        for p in self.get_players():
            if p.auctioneer:
                p.set_auctioneer_payoff()
            else:
                p.set_trader_payoff()

    def get_available_auctions(self):
        # TODO: filter those where price is set?
        return list(self.auctions.all())

    @property
    def traders(self):
        return [p for p in self.get_players() if not p.auctioneer]

    @property
    def auctioneers(self):
        return [p for p in self.get_players() if p.auctioneer]

    def set_winning_bids(self):
        for a in self.auctions.all():
            a.set_winner()

    def mark_trader_winners(self):
        for t in self.traders:
            try:
                t.trader_is_winner = t.bid == t.bid.auction.winner
            except Bid.DoesNotExist:
                pass

    def dump_winning_prices(self):
        for a in self.auctioneers:
            if a.auction.winner:
                a.auc_price = a.auction.winner.price

    def is_auction_available(self, selling):
        return self.auctions.filter(selling_auction=selling).exists()


class Player(BasePlayer):
    bid_dump = models.CurrencyField()
    trader_is_winner = models.BooleanField()
    auc_price = models.CurrencyField()
    auctioneer = models.BooleanField(doc='If yes, a player organizes the auction, not participates in it',
                                     choices=Constants.AUCTIONEER_CHOICES)
    evaluation = models.CurrencyField(doc='individual randomly generated estimation of a good')
    direction = models.IntegerField(choices=(-1, 1))

    def role(self):
        if self.id_in_group <= Constants.num_sellers:
            return Constants.seller
        return Constants.buyer

    def is_selling_auction_type(self):
        return self.role() == Constants.seller

    def is_auction_available(self):
        return self.group.is_auction_available(selling=self.role() == Constants.buyer)

    def get_payoff(self, price):
        return self.direction * (price - self.evaluation)

    def set_auctioneer_payoff(self):
        self.payoff = Constants.earning_if_none
        try:
            winner = self.auction.winner
            if winner:
                self.payoff = self.get_payoff(winner.price)
        except Auction.DoesNotExist:
            pass

    def set_trader_payoff(self):
        self.payoff = Constants.earning_if_none
        try:
            b = self.bid
            if b == b.auction.winner:
                self.payoff = self.get_payoff(b.price)
        except Bid.DoesNotExist:
            pass


class Auction(djmodels.Model):
    selling_auction = models.BooleanField(doc='if true, this is an auction to sell good (so the highest bid wins')
    market = djmodels.ForeignKey(to=Group, related_name='auctions')
    auctioneer = djmodels.OneToOneField(to=Player, related_name='auction')
    winner = djmodels.OneToOneField(to='Bid', related_name='winner_bid', null=True)

    def __str__(self):
        selling = 'Selling' if self.selling_auction else 'Buying'
        return f'{selling} auction with baseline {self.auctioneer.evaluation}'

    def set_winner(self):
        """
        Set the winner for this auction if any exists.

        :return: None.
        """
        bids = self.bids.filter(price__isnull=False)
        f = Max if self.selling_auction else Min
        # if this is the selling auction we need to get the item with max price, and with min price otherwise.
        winning_price = bids.aggregate(m=f('price')).get('m')

        if winning_price:
            winners = bids.filter(price=winning_price)
            # we need this BS because of ties.
            self.winner = random.choice(winners)
            self.save()


class Bid(djmodels.Model):
    auction = djmodels.ForeignKey(to=Auction, related_name='bids', null=True)
    bidder = djmodels.OneToOneField(to=Player, related_name='bid')
    price = models.CurrencyField()
