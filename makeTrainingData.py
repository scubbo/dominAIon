#!/usr/bin/env python3

import os
import sys
import json


def go():
    if not os.path.exists('trainingData'):
        os.mkdir('trainingData')

    with open('runs/run_1') as f:  # TODO - parameterize!
        game_data = json.load(f)

    score1, score2 = game_data['score'].split(':')
    if score1 == score2:
        print('Game was a draw - exiting')
        sys.exit(0)  # Not sure what we should do in the situation of a draw

    winning_player = 1 if score1 > score2 else 2

    for move in game_data['moves']:
        situation = move['gamestate_view'][-1]
        input_vector = move['gamestate_view'][:-1]
        output_vector = build_output_vector(situation, move['action_index'])
        if move['player'] == winning_player:
            with open('trainingData/data_1', 'a') as f:
                f.write(json.dumps(input_vector) + ':::' + json.dumps(output_vector) + '\n')


# TODO - shouldn't share the knowledge of "how to construct a situation-specific output vector"
# here (that is - how long it should be). Probably, encode it in the situations themselves
# and have both this and RandomStrategy reference it.
# TODO - the hardcoded "11"s here are wrong, they should be number_of_cards (which, in a standard
# game, would probably be 16, or 17 if curses)
def build_output_vector(situation, target_index):
    if situation == 0:
        # 10 = number_of_cards
        return [1 if index == target_index else 0 for index in range(11 + 1)]
    if situation == 1:
        return [1 if index == target_index else 0 for index in range(2 * 11 + 1)]
    if situation == 2:
        return [1]  # there is not, currently, any way to do anything other than pass the turn on cleanup


if __name__ == '__main__':
    go()




