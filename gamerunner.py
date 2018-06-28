import os

class Gamerunner:
  def __init__(self, strategy_1, strategy_2, gamemaster):
    self.strategy_1 = strategy_1
    self.strategy_2 = strategy_2
    self.gamemaster = gamemaster
    self.gamestate = gamemaster.gamestate #todo - for proper OO-ness, should probably make this an argument of methods of gamemaster

  def main(self):

    run_iteration = self.make_directory_for_persistence()

    current_player = 1
    situation = 0
    # TODO - technically, the game only ends at the end of the turn in which this becomes true, not immediately.
    while not self.has_game_ended():
      # Currently only supports two players
      gamestate_view, number_of_cards = self.gamestate.serialize(current_player, situation)
      proposed_action = getattr(self, 'strategy_'+str(current_player)).determine_action(gamestate_view, number_of_cards)

      attempts = 0
      while attempts < 3:
        try:
          print('With gamestate ' + str(self.gamestate) + '\nSituation: ' + str(situation) + '\nPlayer ' + str(current_player) + ' proposed ' + str(proposed_action))
          input('>>')
          situation = getattr(self.gamemaster, proposed_action[0])(current_player, situation, *proposed_action[1])
          break
        except Exception as e:
          with open('runs/run_' + str(run_iteration) + '/failed_actions.txt', 'a') as f:
            f.write(str(current_player) + ':' + self.gamestate.to_json() + '->' + str(proposed_action) + '\n') # For now this works, but might need custom serialization logic if actions get more complex
          attempts += 1
      else:
        print('Strategy could not determine a legal move from gamestate ' + str(self.gamestate) + ' - aborting')
        raise Exception()

      with open('runs/run_' + str(run_iteration) + '/actions_' + str(current_player) + '.txt', 'a') as f:
        f.write(str(current_player) + ':' + self.gamestate.to_json() + '->' + str(proposed_action) + '\n')

      # TODO: once we get more complex and add reaction cards,
      # or choices that can be made on other players' turns,
      # this will need to be more nuanced and include both
      # "active player" (the player making the decision) and
      # "current player" (the player whose turn it is)
      if self.gamestate.phase.startswith('action'):
        current_player = int(self.gamestate.phase[-1])

    player_1_score, player_2_score = self.gamemaster.determine_scores()
    print('Score: ' + str(player_1_score) + ':' + str(player_2_score))
    with open('runs/run_' + str(run_iteration) + '/final_score.txt', 'a') as f:
      f.write(str(player_1_score) + ':' + str(player_2_score))
  
  def has_game_ended(self):
    return len([pile for pile in self.gamestate.supply if pile == 0]) >= 3 or self.gamestate.supply[5] == 0

  def make_directory_for_persistence(self):
    if 'runs' not in os.listdir('.'):
      os.mkdir('runs')

    runs = os.listdir('runs')
    if not runs:
      current_iteration = 1
    else:
      current_iteration = max(map(lambda x: int(x[4:]), runs))+1

    os.mkdir('runs/run_'+str(current_iteration))
    return current_iteration


def make_basic():
  from cards import cards
  from strategies.randomStrategy import RandomStrategy
  from gamemaster import Gamemaster

  strat_1 = RandomStrategy(cards, 1)
  strat_2 = RandomStrategy(cards, 2)
  gamemaster = Gamemaster(cards)
  return Gamerunner(strat_1, strat_2, gamemaster)
