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
            proposed_actions_as_vector = getattr(self, 'strategy_' + str(current_player)).determine_action(
                                                                                                gamestate_view,
                                                                                                number_of_cards)
            proposed_actions = self._interpret_vectorized_action_proposals(situation, proposed_actions_as_vector)

            attempt = 0
            while attempt < 3:  # TODO - consider increasing this when we go to truly randomized RNNs!
                try:
                    # We track original_index since it will be used in training RNNs -
                    # it is the "outcome" that the RNN generated
                    proposed_action, original_index, args = proposed_actions[attempt]
                    print('With gamestate ' + str(self.gamestate) + '\nSituation: ' + str(
                        situation) + '\nPlayer ' + str(current_player) + ' proposed ' + str(proposed_action) + '(' +
                        str(args) + ')')
                    if self.wait_for_input:
                        input('>>')
                    situation = proposed_action(current_player, situation, *args)
                    break
                except Exception as e:
                    print(e)
                    game_record['failed_moves'].append(
                        {
                            'player': current_player,
                            'gamestate_view': gamestate_view,
                            'proposed_action_human_readable_name': str(proposed_action),
                            'proposed_action_human_readable_args': args,
                            'proposed_action_index': original_index
                        })
                    attempt += 1
            else:
                print('Strategy could not determine a legal move from gamestate ' + str(self.gamestate) + ' - aborting')
                raise Exception()

            game_record['moves'].append(
                {
                    'player': current_player,
                    'gamestate_view': gamestate_view,
                    'action_human_readable_name': str(proposed_action),
                    'action_human_readable_args': args,
                    'action_index': original_index
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

    # TODO - as situations get more numerous, this should probably be put into situation configuration
    # in fact, the lambda inside the map is the perfect entity to be extracted!
    def _interpret_vectorized_action_proposals(self, situation, proposed_actions):
        if situation == 0:
            ordered_indices = [x[0] for x in sorted(enumerate(proposed_actions), key=lambda x: x[1], reverse=True)]
            return list(map(
                lambda index:
                    (self.gamemaster.play_action, index, [index])
                    if index != len(proposed_actions)-1
                    else (self.gamemaster.end_phase, len(proposed_actions)-1, []),
                ordered_indices
            ))
        if situation == 1:
            ordered_indices = [x[0] for x in sorted(enumerate(proposed_actions), key=lambda x: x[1], reverse=True)]
            return self._parse_buy_phase_vectored_actions_into_methods(ordered_indices)
        if situation == 2:
            return [(self.gamemaster.end_phase, 0, [])]
        raise Exception('Don\'t know how to do that yet!')

    def _parse_buy_phase_vectored_actions_into_methods(self, proposed_action_indices):
        output_list = []
        maximal_treasure_index = int((len(proposed_action_indices)-1)/2)-1
        end_phase_index = len(proposed_action_indices)-1
        for index in proposed_action_indices:
            if index <= maximal_treasure_index:
                output_list.append((self.gamemaster.play_treasure, index, [index]))
            elif index == end_phase_index:
                output_list.append((self.gamemaster.end_phase, end_phase_index, []))
            else:
                output_list.append((self.gamemaster.buy_card, index, [index-(maximal_treasure_index+1)]))
        return output_list


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
