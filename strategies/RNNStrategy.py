import random
import string


class RNNStrategy:

    def __init__(self, cards, player_number):
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits) for _ in range(10))
        self.RNNs = make_rnns(cards)


# TODO - make this aware of `cards`, since strategies will be different
# depending on the card pool.
# For now, this just makes one RNN-per-situation
def make_rnns(cards):
    import situations
