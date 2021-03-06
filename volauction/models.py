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
So if a person has an auction he owns. but there is no winner, that automatically means that no one participated. That 
is the first situation when an individual is forwarded to NoAuction page.

2. A person decides to be a trader, but there are no auctions to attend.
"""

########### BLOCK: ERROR MESSAGES ##############################################################
SELLERS_ERR_MSG = 'Number of sellers per group should be less than total number of market participants.'
GROUP_SIZE_ERR_MSG = 'Number of participants in session should be divisible by the group size.'


############ END OF: ERROR MESSAGES #############################################################


class Constants(BaseConstants):
    name_in_url = 'volauction'
    players_per_group = None
    num_rounds = 1
    buyer, seller = 'Buyer', 'Seller'  # keep role names here so we can change them later in one spot
    AUCTIONEER_CHOICES = [(True, 'Auctioneer'), (False, 'Participant in someone\'s auction')]
    lb, ub = 0, 10  # lower and upper boundaries of evaluation
    earning_if_none = 0  # Earnings of traders and auctioneers if no auction is won or happened


class Subsession(BaseSubsession):
    group_size = models.IntegerField(doc='number of total participants (sellers+buyers')
    num_sellers = models.IntegerField(doc='number of sellers')
    num_buyers = models.IntegerField(doc='number of buyers')

    def creating_session(self):
        ########### BLOCK: Checking group size ##############################################################
        self.num_sellers = self.session.config['num_sellers']
        self.num_buyers = self.session.config['num_buyers']
        self.group_size = self.num_buyers + self.num_sellers
        tot_participants = self.session.num_participants
        assert tot_participants % self.group_size == 0, GROUP_SIZE_ERR_MSG
        ############ END OF: Checking group size #############################################################

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

    @property
    def traders(self):
        return [p for p in self.get_players() if not p.auctioneer]

    @property
    def auctioneers(self):
        return [p for p in self.get_players() if p.auctioneer]

    def set_winning_bids(self):
        """
        Loop through group's auctions and set the winner (if any).

        :return: None
        :rtype: None
        """
        for a in self.auctions.all():
            a.set_winner()

    def mark_trader_winners(self):
        """
        Dump winners to the oTree player's model so they can be exported later.

        :return:None
        :rtype: None
        """
        for t in self.traders:
            try:
                t.trader_is_winner = t.bid == t.bid.auction.winner
            except Bid.DoesNotExist:
                pass

    def dump_winning_prices(self):
        """
        Dump winning prices to the db for export.

        :return: None
        :rtype: None
        """
        for a in self.auctioneers:
            if a.auction.winner:
                a.auc_price = a.auction.winner.price


class Player(BasePlayer):
    bid_dump = models.CurrencyField()
    trader_is_winner = models.BooleanField()
    auc_price = models.CurrencyField()
    auctioneer = models.BooleanField(doc='If yes, a player organizes the auction, not participates in it',
                                     choices=Constants.AUCTIONEER_CHOICES)
    evaluation = models.CurrencyField(doc='individual randomly generated estimation of a good')
    direction = models.IntegerField(choices=(-1, 1))

    def role(self):
        if self.id_in_group <= self.subsession.num_sellers:
            return Constants.seller
        return Constants.buyer

    def is_selling_auction_type(self):
        return self.role() == Constants.seller

    def get_available_auctions(self):
        """
        Return all auctions of the group for this type of players.

        :return: Queryset with available auctions.
        :rtype: queryset
        """
        return  self.group.auctions.filter(selling=self.role() == Constants.buyer)

    def is_auction_available(self):
        """
        Checking if the group has an auction of a corresponding type.

        :return: Yes, if a group has an auction to participate in of a type correspodning to a player's role.
        :rtype: bool
        """
        return self.get_available_auctions().exists()

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
    selling = models.BooleanField(doc='if true, this is an auction to sell good (so the highest bid wins')
    market = djmodels.ForeignKey(to=Group, related_name='auctions')
    auctioneer = djmodels.OneToOneField(to=Player, related_name='auction')
    winner = djmodels.OneToOneField(to='Bid', related_name='winner_bid', null=True)

    def __str__(self):
        selling = 'Selling' if self.selling else 'Buying'
        minimax = 'minimum' if self.selling else 'maximum'
        # we pass pk here to distinguish between auctions with the same evaluation.
        return f'#{self.pk}: {selling} auction at {minimax} {self.auctioneer.evaluation}'

    def set_winner(self):
        """
        Set the winner for this auction if any exists.

        :return: None.
        """
        bids = self.bids.filter(price__isnull=False)
        f = Max if self.selling else Min
        # if this is the selling auction we need to get the item with max price, and with min price otherwise.
        winning_price = bids.aggregate(m=f('price')).get('m')

        if winning_price:
            winners = bids.filter(price=winning_price)
            # we need this BS  to solve possible ties.
            self.winner = random.choice(winners)
            self.save()


class Bid(djmodels.Model):
    auction = djmodels.ForeignKey(to=Auction, related_name='bids', null=True)
    bidder = djmodels.OneToOneField(to=Player, related_name='bid')
    price = models.CurrencyField()
