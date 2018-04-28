from deck import Deck
from json import dumps, JSONEncoder

phase_order = ['action_1', 'buy_1', 'cleanup_1', 'action_2', 'buy_2', 'cleanup_2']

class Gamestate:
  # Does not currently allow for multiple players
  def __init__(
      self,
      supply,
      deck_1, hand_1, play_1, discard_1,
      deck_2, hand_2, play_2, discard_2,
      trash,
      phase,
      bought_so_far_this_turn):
    self.supply = supply
    self.deck_1 = deck_1 # TODO - bot should not have knowledge of the order of decks!
    self.hand_1 = hand_1
    self.play_1 = play_1
    self.discard_1 = discard_1
    self.deck_2 = deck_2
    self.hand_2 = hand_2
    self.play_2 = play_2
    self.discard_2 = discard_2
    self.trash = trash
    self.phase = phase
    self.bought_so_far_this_turn = bought_so_far_this_turn

  def __str__(self):
    return 'Supply: ' + str(self.supply) + '\nDeck: ' + str(self.deck_1.cards[:5]) + "...\nHand: " + str(self.hand_1) + "\nPlay: " + str(self.play_1) + '\nDiscard: ' + str(self.discard_1) + '\nPhase: ' + str(self.phase)

  def to_json(self):
    return dumps(self.__dict__, cls=GamestateEncoder)

  def player_1_draw(self):
    # Todo - messaging
    try:
      self.hand_1.append(self.deck_1.draw_card())
      return self
    except IndexError:
      # Tried to pop from an empty list - that is, draw from an empty deck
      self.deck_1 = Deck(self.discard_1)
      self.discard_1 = []
      return self.player_1_draw()

  def player_2_draw(self):
    try:
      self.hand_2.append(self.deck_2.draw_card())
      return self
    except IndexError:
      # Tried to pop from an empty list - that is, draw from an empty deck
      self.deck_2 = Deck(self.discard_2)
      self.discard_2 = []
      return self.player_2_draw()

  def player_1_draw_hand(self):
    for i in range(5):
      self.player_1_draw()
    return self

  def player_2_draw_hand(self):
    for i in range(5):
      self.player_2_draw()
    return self

  def play_card(self, index):
    # Note - this *is* atomic, since removal is the only thing that can fail
    self.hand_1.remove(index)
    self.play_1.append(index)
    return self

  def buy_card(self, index):
    if self.supply[index] > 0:
      self.supply[index] -= 1
      self.discard_1.append(index)
      self.bought_so_far_this_turn.append(index)
    else:
      raise ValueError

  def get_next_phase(self):
    try:
      return phase_order[phase_order.index(self.phase)+1]
    except IndexError:
      return phase_order[0]

  def cleanup_1(self):
    while (True):
      try:
        self.discard_1.append(self.play_1.pop())
      except IndexError:
        break
    while (True):
      try:
        self.discard_1.append(self.hand_1.pop())
      except IndexError:
        break
    self.player_1_draw_hand()
    self.bought_so_far_this_turn = []

  # This should probably be a "static" method,
  # but then Interpreter would have to import Gamestate
  def get_index_of_current_phase(self):
    return phase_order.index(self.phase)

  def serialize_for_player(self, player_number):
    if player_number not in [1, 2]:
      raise ValueError("Haven't done that yet")

    number_of_cards = len(self.supply)

    vector = []
    vector += self.supply
    if player_number == 1:
      vector += self._vectorize_subset(self.deck_1.contents(), number_of_cards)
      vector += self._vectorize_subset(self.hand_1, number_of_cards)
      vector += self._vectorize_subset(self.play_1, number_of_cards)
      vector += self._vectorize_subset(self.discard_1, number_of_cards)
      # We concatenate the opponent's deck and hand because we don't know what's where
      vector += self._vectorize_subset(self.deck_2.contents()+self.hand_2, number_of_cards)
      vector += self._vectorize_subset(self.discard_2, number_of_cards)
      vector += self._vectorize_subset(self.trash, number_of_cards)
      vector += self._vectorize_subset(self.bought_so_far_this_turn, number_of_cards)
      vector += [self.get_index_of_current_phase()]
    elif player_number == 2:
      vector += self._vectorize_subset(self.deck_2.contents(), number_of_cards)
      vector += self._vectorize_subset(self.hand_2, number_of_cards)
      vector += self._vectorize_subset(self.play_2, number_of_cards)
      vector += self._vectorize_subset(self.discard_2, number_of_cards)
      # We concatenate the opponent's deck and hand because we don't know what's where
      vector += self._vectorize_subset(self.deck_1.contents()+self.hand_1, number_of_cards)
      vector += self._vectorize_subset(self.discard_1, number_of_cards)
      vector += self._vectorize_subset(self.trash, number_of_cards)
      vector += self._vectorize_subset(self.bought_so_far_this_turn, number_of_cards)
      # Cycle this offset by 3 because, as far as player 2 is concerned, their action phase *is* the first one
      vector += [(self.get_index_of_current_phase()+3)%6]

    return vector, number_of_cards

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

def create_initial_gamestate(supply, deck_1, deck_2):
  initial_gamestate = Gamestate(supply, deck_1, [], [], [], deck_2, [], [], [], [], phase_order[0], [])
  initial_gamestate.player_1_draw_hand()
  return initial_gamestate

# https://stackoverflow.com/a/3768975/1040915
class GamestateEncoder(JSONEncoder):
  def default(self, o):
    if type(o) is Deck:
      return dumps(o.__dict__)
    return JSONEncoder.default(self, o)

