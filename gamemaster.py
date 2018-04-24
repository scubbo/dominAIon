import gamestate
from deck import Deck

class Gamemaster:
  def __init__(self, cards):
    self.cards = cards
    for index, card in enumerate(cards):
      if card['name'] == 'Copper':
        copper_index = index
        continue
      if card['name'] == 'Estate':
        estate_index = index

    self.gamestate = self.build_initial_gamestate(copper_index, estate_index)
    print('Your hand is ' + self.pretty_print_hand() + ' and you are in the ' + self.gamestate.phase + ' phase.')

  def build_initial_gamestate(self, copper_index, estate_index):
    supply = self._make_supply()
    deck_1, deck_2 = self._make_decks(copper_index, estate_index)
    return gamestate.create_initial_gamestate(supply, deck_1, deck_2)

  # TODO: parameterization
  def get_hand_1(self):
    return self.gamestate.hand_1

  def pretty_print_hand(self):
    return ','.join([self.cards[i]['name'] for i in self.gamestate.hand_1])

  def play_action(self, index):
    self._check_for_phase('action_1')

    card = self.cards[index]
    if card['type'] != 'action':
      raise ValueError(card['name'] + ' is not an action!')

    try:
      self.gamestate.play_card(index)
    except ValueError:
      raise ValueError('No ' + card['name'] + ' in hand!')

  def play_treasure(self, index):
    self._check_for_phase('buy_1')

    card = self.cards[index]
    if card['type'] != 'treasure':
      raise ValueError(card['name'] + ' is not a treasure!')

    try:
      self.gamestate.play_card(index)
    except ValueError:
      raise ValueError('No ' + card['name'] + ' in hand!')

  #TODO - should bought_so_far be in Gamestate?
  #Probably not - try to make it *just* about presence/absence/count of cards
  #(By which logic, keeping cost calculation here is correct)
  def buy_card(self, index, bought_so_far):
    self._check_for_phase('buy_1')

    card = self.cards[index]
    cost = card['cost']
    total_cost = sum([self.cards[index]['cost'] for index in bought_so_far+[index]])
    total_coins = self._get_total_coins()
    if total_cost > total_coins:
      raise ValueError('Cannot afford that!')

    try:
      self.gamestate.buy_card(index)
    except ValueError:
      raise ValueError('No ' + card['name'] + ' left in supply!')

  def end_phase(self, verbose=False):
    current_phase = self.gamestate.phase
    next_phase = self.gamestate.get_next_phase()
    # TODO - logic for cleanup
    self.gamestate.phase = next_phase
    if verbose:
      print('You just ended the ' + current_phase + ' phase and are now in the ' + next_phase + ' phase')
    if self.gamestate.phase == 'cleanup_1':
      # TODO - for cards that trigger on discarding, this will need to execute some logic
      self.gamestate.cleanup_1()
      if verbose:
        print('Cleaned up')

  def _make_supply(self, number_of_players=2):
    supply = []
    for card in self.cards:
      if card['name'] == 'Copper':
        supply.append(60-(7*number_of_players))
        continue
      if card['name'] == 'Silver':
        supply.append(40)
        continue
      if card['name'] == 'Gold':
        supply.append(30)
      if card['type'] == 'victory':
        if number_of_players == 2:
          supply.append(8)
        else:
          supply.append(12)
        continue
      if card['type'] == 'action':
        supply.append(10)
    return supply

  def _make_decks(self, copper_index, estate_index, number_of_decks=2):
    response = []
    for i in range(number_of_decks):
      response.append(Deck([copper_index]*7 + [estate_index]*3))
    return response

  def _check_for_phase(self, phase):
    if self.gamestate.phase != phase:
      raise ValueError('Now is not the time to use that')

  def _get_total_coins(self):
    total_coins = 0
    for index in self.gamestate.play_1:
      card = self.cards[index]
      if card['type'] == 'treasure':
        total_coins += card['value']
        continue
      if card['type'] == 'action' and 'coins' in card['action']:
        total_coins += card['action']['coins']
    return total_coins


