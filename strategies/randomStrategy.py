import random

class RandomStrategy:

  # This Strategy needs to know what the cards
  # *are*, because it tries to bias for legal
  # actions (a true RNN strategy wouldn't do so,
  # but only because it would learn to avoid
  # illegal actions over time)
  def __init__(self, cards):
    self.cards = cards

  def determine_action(self, gamestate):
    if gamestate.phase == 'action_1':
      if random.random() < 0.8:
        actions_remaining = self._determine_actions_remaining(gamestate)
        actions_in_hand = [index for index in gamestate.hand_1 if self.cards[index]['type'] == 'action']
        if actions_remaining > 0 and actions_in_hand:
          return ('play_action', [random.choice(actions_in_hand)])

    if gamestate.phase == 'buy_1':
      if random.random() < 0.9:
        # It will rarely be suboptimal for this strategy to play all treasures, given that there's nothing
        # in the first sets of cards that I'll be adding which require treasure in-hand at the point of buying
        treasure_in_hand = [index for index in gamestate.hand_1 if self.cards[index]['type'] == 'treasure']
        if treasure_in_hand:
          return ('play_treasure', [random.choice(treasure_in_hand)])

        # There is no notion of "buys remaining" given this degree of information,
        # since gamestate doesn't encode "number of buys used this phase".
        # Maybe that needs to change.
        #
        # As it stands, we'll simply return a desired action,
        # and Gamemaster can handle determining if it's illegal
        # (which is something it will need to be able to do *anyway*,
        # for when we move to RNN-based strategies)
        coins = self._determine_coins_available(gamestate)
        print('coins is ' + str(coins))
        buy_targets = self._pick_affordable_buy_targets(coins, gamestate)
        print('buy_targets is ' + str(buy_targets))
        if buy_targets:
          return ('buy_card', [random.choice(buy_targets)])

    return ('end_phase', [])


  def _determine_actions_remaining(self, gamestate):
    remaining = 1
    for action_played_index in gamestate.play_1:
      card = self.cards[action_played_index]
      # This should only be called in the action
      # phase, so every card played *should* only be
      # an action, but since we're having to get the card-data
      # anyway, might as well check just in case...
      if card['type'] == 'action':
        remaining -= 1
        if 'actions' in card['action']:
          remaining += card['action']['actions']
    return remaining

  def _determine_coins_available(self, gamestate):
    available = 0
    for index_played in gamestate.play_1:
      card = self.cards[index_played]
      if card['type'] == 'treasure':
        available += card['value']
        continue
      if card['type'] == 'action' and 'coins' in card['action']:
        available += card['action']['coins']
    return available

  def _pick_affordable_buy_targets(self, coins, gamestate):
    return [index for index in range(len(gamestate.supply)) if gamestate.supply[index] > 0 and self.cards[index]['cost'] < coins]