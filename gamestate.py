phase_order = ['action_1', 'buy_1', 'cleanup_1', 'action_2', 'buy_2', 'cleanup_2']

class Gamestate:
  # Does not currently allow for multiple players
  def __init__(
      self,
      supply,
      deck_1, hand_1, play_1, discard_1,
      deck_2, hand_2, play_2, discard_2,
      trash,
      phase):
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

  def __str__(self):
    return str(self.supply) + ':' + str(self.deck_1.cards[:5]) + "...:" + str(self.hand_1) + ":" + str(self.play_1) + ":" + str(self.discard_1)

  def player_1_draw(self):
    # TODO: reshuffles (and messaging)
    self.hand_1.append(self.deck_1.draw_card())
    return self

  def player_2_draw(self):
    # TODO: reshuffles (and messaging)
    self.hand_2.append(self.deck_2.draw_card())
    return self

  def player_1_draw_hand(self):
    for i in range(5):
      self.hand_1.append(self.deck_1.draw_card())
    return self

  def player_2_draw_hand(self):
    for i in range(5):
      self.hand_2.append(self.deck_2.draw_card())
    return self

  def play_card(self, index):
    # Note - this *is* atomic, since removal is the only thing that can fail
    self.hand_1.remove(index)
    self.play_1.append(index)

  def buy_card(self, index):
    if self.supply[index] > 0:
      self.supply[index] -= 1
      self.discard_1.append(index)
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

  # This should probably be a "static" method,
  # but then Interpreter would have to import Gamestate
  def get_index_of_current_state(self):
    return phase_order.index(self.phase)

def create_initial_gamestate(supply, deck_1, deck_2):
  initial_gamestate = Gamestate(supply, deck_1, [], [], [], deck_2, [], [], [], [], phase_order[0])
  initial_gamestate.player_1_draw_hand()
  return initial_gamestate
