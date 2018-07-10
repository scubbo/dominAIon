import os
import json


class Gamerunner:
    def __init__(self, strategy_1, strategy_2, gamemaster, wait_for_input=False):
        self.strategy_1 = strategy_1
        self.strategy_2 = strategy_2
        self.gamemaster = gamemaster
        # todo - for proper OO-ness, should probably make this an argument of methods of gamemaster
        self.gamestate = gamemaster.gamestate
        self.wait_for_input = wait_for_input

    def main(self):

        self.make_directory_for_persistence()
        game_record = {
            'strat_1_id': self.strategy_1.id,
            'strat_2_id': self.strategy_2.id,
            'moves': [],
            'failed_moves': []
        }
        # TODO - Need to record the universe-of-cards that this was run on

        current_player = 1
        situation = 0
        # TODO - technically, the game only ends at the end of the turn in which this becomes true, not immediately.
        while not self.has_game_ended():
            # Currently only supports two players
            gamestate_view, number_of_cards = self.gamestate.serialize(current_player, situation)
            proposed_action = getattr(self, 'strategy_' + str(current_player)).determine_action(gamestate_view,
                                                                                                number_of_cards)

            attempts = 0
            while attempts < 3:
                try:
                    print('With gamestate ' + str(self.gamestate) + '\nSituation: ' + str(
                        situation) + '\nPlayer ' + str(current_player) + ' proposed ' + str(proposed_action))
                    if self.wait_for_input:
                        input('>>')
                    situation = getattr(self.gamemaster, proposed_action[0])(current_player, situation,
                                                                             *proposed_action[1])
                    break
                except Exception:
                    game_record['failed_moves'].append(
                        str(current_player) + ':' + self.gamestate.to_json() + '->' + str(
                            # For now this works, but might need custom serialization logic if actions get more complex
                            proposed_action))
                    attempts += 1
            else:
                print('Strategy could not determine a legal move from gamestate ' + str(self.gamestate) + ' - aborting')
                raise Exception()

            game_record['moves'].append(
                {
                    'player': current_player,
                    'gamestate_view': gamestate_view,
                    'proposed_action': proposed_action
                }
            )
            # TODO: once we get more complex and add reaction cards,
            # or choices that can be made on other players' turns,
            # this will need to be more nuanced and include both
            # "active player" (the player making the decision) and
            # "current player" (the player whose turn it is)
            if self.gamestate.phase.startswith('action'):
                current_player = int(self.gamestate.phase[-1])

        # Note the lack of a `try-finally` wrapping this `while` loop. Let's not record moved from a game
        # that didn't end, because then there's no way to tell which were "good" ones.

        player_1_score, player_2_score = self.gamemaster.determine_scores()
        print('Score: ' + str(player_1_score) + ':' + str(player_2_score))
        game_record['score'] = str(player_1_score) + ':' + str(player_2_score)

        runs = os.listdir('runs')
        if not runs:
            current_iteration = 1
        else:
            current_iteration = max(map(lambda x: int(x[4:]), runs)) + 1

        with open('runs/run_' + str(current_iteration), 'a') as f:
            f.write(json.dumps(game_record))

    def has_game_ended(self):
        return len([pile for pile in self.gamestate.supply if pile == 0]) >= 3 or self.gamestate.supply[5] == 0

    @staticmethod
    def make_directory_for_persistence():
        if 'runs' not in os.listdir('.'):
            os.mkdir('runs')


def make_basic():
    return Gamerunner(*_make_basic_underlying(), True)


def make_basic_automated():
    return Gamerunner(*_make_basic_underlying())


def _make_basic_underlying():
    from cards import cards
    from strategies.randomStrategy import RandomStrategy
    from gamemaster import Gamemaster

    strat_1 = RandomStrategy(cards, 1)
    strat_2 = RandomStrategy(cards, 2)
    gamemaster = Gamemaster(cards)
    return strat_1, strat_2, gamemaster
