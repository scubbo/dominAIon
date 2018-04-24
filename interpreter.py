class Interpreter:
  def __init__(self, strategy, cards, gamestate):
    self.strategy = strategy
    self.cards = cards
    self.gamestate = gamestate
    self.number_of_cards = len(cards)

  def take_action(self):
    vectorized_state = self._vectorize_state()
    # action = strategy.[...]

  # Returns a vector of length 9n+2 (where n is the number of cards),
  # encoding the state known to player 1
  #
  # Some notable things that are not directly encoded:
  # * The turn number (though the game progress can be inferred from number of cards remaining in supply, assuming both players buy cards with any degree of regularity)
  # * The number of coins that the player has available (can be *sort of* inferred from hand/play, though only if indices always match to the same card between playthroughs, by learning which sets lead to "cannot afford that")
  # * How many victory points each player has (sorta-ditto above)
  def _vectorize_state(self):

    vector = []
    vector += self.gamestate.supply

    vector += self._vectorize_subset(self.gamestate.deck_1.contents, self.number_of_cards)
    vector += self._vectorize_subset(self.gamestate.hand_1, self.number_of_cards)
    vector += self._vectorize_subset(self.gamestate.play_1, self.number_of_cards)
    vector += self._vectorize_subset(self.gamestate.discard_1, self.number_of_cards)

    vector += self._vectorize_subset(self.gamestate.deck_2.contents, self.number_of_cards)
    vector += [len(self.gamestate.hand_2)]
    vector += self._vectorize_subset(self.gamestate.play_2, self.number_of_cards)
    vector += self._vectorize_subset(self.gamestate.discard_2, self.number_of_cards)
    vector += self._vectorize_subset(self.gamestate.trash, self.number_of_cards)
    vector += [self.gamestate.get_index_of_current_state()]

    return vector

  # Creates a vector of length equal to number of cards,
  # wherein the i-th value is how many of the i-th card
  # are in the subset
  #
  # e.g. [1,2,1,6,8,3,1,3] => [0, 3, 1, 2, 0, 0, 1, 0, 1, 0, ...]
  def _vectorize_subset(self, subset, length):
    vector = [0] * length
    for i in subset:
      vector[i] += 1
    return vector

