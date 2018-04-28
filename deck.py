from random import shuffle

class Deck:
  def __init__(self, cards, should_shuffle=True):
    self.sorted_cards = sorted(cards)
    if should_shuffle:
      shuffle(cards)
    self.cards = cards

  def draw_card(self):
    index = self.cards.pop()
    self.sorted_cards.remove(index)
    return index

  def contents(self):
    # Note that this does *not* represent the actual order of the deck!
    return self.sorted_cards