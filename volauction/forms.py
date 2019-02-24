from django import forms
from .models import Bid, Auction
from utils import cp
from django.forms import ModelChoiceField


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['auction', 'price']

    def __init__(self, *args, **kwargs):
        kwargs.pop('view')  # todo: why oTree passes view here? may be needed for bots
        super().__init__(*args, **kwargs)
        bid = kwargs['instance']
        player = bid.bidder
        group = player.group
        # We need to inverse selling auction type so buyers would see selling auctions, and sellers would see
        # buying auctions
        auction_type = not player.is_selling_auction_type()
        self.fields['auction'] = forms.ModelChoiceField(
            queryset=Auction.objects.filter(market=group,
                                            selling_auction=auction_type,
                                            ).exclude(auctioneer=player))
