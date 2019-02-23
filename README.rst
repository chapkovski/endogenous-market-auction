Endogenous auction formation
============================

:Author:
    Philipp Chapkovski (HSE-Moscow), chapkovski@gmail.com

The market space consists of two types of participants:

- buyer
- seller

Players of both types have individual, randomly generated valuation of a good.


Each round of the game consists of three stages:

1. Announcement of the role and individual evaluation.

2. A participant chooses whether she would like to participate in someone else's
   auction or to conduct it herself. (see more in `auctioneer` section).

3. Auctions happen: active participants (not auctioneers) make their bids, and the winner
   gets the good.

Profit formation
----------------

Seller's profit:
    Selling price - individual evalution.


Buyer's profit:
    Individual evalution - buying price.


If an active participant (not auctioneer) does not win an auction, her profit is zero.

If there are no participants in the auction, the auctioneer's profit is zero in this round.

Market clearance and conflicts
------------------------------

- If everybody chooses one kind of activity (being an auctioneer or being an
  active participant, then every member of the group gets zero.


