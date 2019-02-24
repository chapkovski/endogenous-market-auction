"""
Data storage and logic for endogeous market formation game.

"""
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
import random

author = 'Philipp Chapkovski, chapkovski@gmail.com HSE-Moscow'

doc = """
Endogenuous market formation. 

"""
########### BLOCK: ERROR MESSAGES ##############################################################
SELLERS_ERR_MSG = 'Number of sellers per group should be less than total number of market participants'


############ END OF: ERROR MESSAGES #############################################################


class Constants(BaseConstants):
    name_in_url = 'volauction'
    # todo: make group size adjustable (see speed_app)
    players_per_group = 3
    num_rounds = 1
    num_sellers = 2
    assert num_sellers < players_per_group, SELLERS_ERR_MSG
    buyer, seller = 'Buyer', 'Seller'  # keep role names here so we can change them later in one spot
    AUCTIONEER_CHOICES = [(True, 'Auctioneer'), (False, 'Participant in someone\'s auction')]
    lb, ub = 0, 10  # lower and upper boundaries of evaluation


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.evaluation = random.uniform(Constants.lb, Constants.ub)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    bid = models.CurrencyField()
    auctioneer = models.BooleanField(doc='If yes, a player organizes the auction, not participates in it',
                                     choices=Constants.AUCTIONEER_CHOICES)
    evaluation = models.CurrencyField(doc='individual randomly generated estimation of a good')

    def role(self):
        if self.id_in_group <= Constants.num_sellers:
            return Constants.seller
        return Constants.buyer

    def is_selling_auction_type(self):
        return self.role() == Constants.seller


class Auction(djmodels.Model):
    selling_auction = models.BooleanField(doc='if true, this is an auction to sell good (so the highest bid wins')
    market = djmodels.ForeignKey(to=Group, related_name='auctions')
    auctioneer = djmodels.OneToOneField(to=Player, related_name='auction')
    winner = djmodels.OneToOneField(to=Player, related_name='auction')

    def __str__(self):
        selling = 'Selling' if self.selling_auction else 'Buying'
        return f'{selling} auction with baseline {self.auctioneer.evaluation}'


class Bid(djmodels.Model):
    auction = djmodels.ForeignKey(to=Auction, related_name='bids', null=True)
    bidder = djmodels.OneToOneField(to=Player, related_name='bids')
    price = models.CurrencyField()
