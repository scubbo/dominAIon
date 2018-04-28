class Gamerunner:
  def __init__(self, strategy_1, strategy_2, gamemaster):
    self.strategy_1 = strategy_1
    self.strategy_2 = strategy_2
    self.gamemaster = gamemaster
    self.gamestate = gamemaster.gamestate #todo - for proper OO-ness, should probably make this an argument of methods of gamemaster

  def main(self):
    current_player = 1
    while not self.has_game_ended():
      # Currently only supports two players
      gamestate_view, number_of_cards = self.gamestate.serialize_for_player(current_player)
      proposed_action = getattr(self, 'strategy_'+str(current_player)).determine_action(gamestate_view, number_of_cards)

      attempts = 0
      while attempts < 3:
        try:
          # TODO - this doesn't currently work:
          # need to make proposed_action be returned unaware of player-ness,
          # and have this code append a "player-number" (and make sure gamestate supported player-indexed methods)
          print('Player ' + str(current_player) + ' proposed ' + str(proposed_action))
          input('')
          getattr(self.gamemaster, proposed_action[0])(*proposed_action[1])
          break
        except Exception as e:
          with open('failed_actions.txt', 'a') as f:
            f.write(str(current_player) + ':' + self.gamestate.to_json() + '->' + str(proposed_action) + '\n') # For now this works, but might need custom serialization logic if actions get more complex
          attempts += 1

      with open('actions_' + str(current_player) + '.txt', 'a') as f:
        f.write(str(current_player) + ':' + self.gamestate.to_json() + '->' + str(proposed_action) + '\n')
      current_player = 3 - current_player
    determine_winner()
  
  def has_game_ended(self):
    return len([pile for pile in self.gamestate.supply if pile == 0]) >= 3 or self.gamestate.supply[5] == 0

  def determine_winner(self):
    pass

def make_basic():
  from cards import cards
  from strategies.randomStrategy import RandomStrategy
  from gamemaster import Gamemaster

  strat_1 = RandomStrategy(cards, 1)
  strat_2 = RandomStrategy(cards, 2)
  gamemaster = Gamemaster(cards)
  return Gamerunner(strat_1, strat_2, gamemaster)
