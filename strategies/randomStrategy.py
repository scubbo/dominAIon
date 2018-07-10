import random


class RandomStrategy:

    # This Strategy needs to know what the cards
    # *are*, because it tries to bias for legal
    # actions (a true RNN strategy wouldn't do so,
    # but only because it would learn to avoid
    # illegal actions over time)
    #
    # id is meaningless for a RandomStrategy,
    # since it is memoryless and so there is
    # no need to refer back to its earlier
    # actions (in a way which *would* be
    # necessary for an RNN, to be sure to train
    # it only on its own moves)
    def __init__(self, cards, player_number):
        self.cards = cards
        self.player_number = player_number
        self.id = 'RandomStrategy'

    def determine_action(self, gamestate_as_vector, number_of_cards):
        gamestate = self.parse_gamestate(gamestate_as_vector, number_of_cards)
        print('Strategy_' + str(self.player_number) + '\'s parsed gamestate view is ' + str(gamestate))
        if gamestate['phase'] == 0:
            if random.random() < 0.8:
                actions_remaining = self._determine_actions_remaining(gamestate)
                actions_in_hand = [index for index in gamestate['hand_1'] if self.cards[index]['type'] == 'action']
                if actions_remaining > 0 and actions_in_hand:
                    return 'play_action', [random.choice(actions_in_hand)]

        if gamestate['phase'] == 1:
            if random.random() < 0.9:
                # It will rarely be suboptimal for this strategy to play all treasures, given that there's nothing
                # in the first sets of cards that I'll be adding which require treasure in-hand at the point of buying
                treasure_in_hand = [index for index in gamestate['hand_1'] if self.cards[index]['type'] == 'treasure']
                if treasure_in_hand:
                    return 'play_treasure', [random.choice(treasure_in_hand)]

                buys_remaining = self._determine_buys_remaining(gamestate)
                if buys_remaining > 0:
                    coins = self._determine_coins_available(gamestate)
                    spent_so_far_this_turn = self._determine_spent_so_far_this_turn(gamestate)
                    buy_targets = self._pick_affordable_buy_targets(coins - spent_so_far_this_turn, gamestate)
                    if buy_targets:
                        return 'buy_card', [random.choice(buy_targets)]

        return 'end_phase', []

    # TODO - arguably, this could belong in gamestate,
    # but ideally nothing else but RandomStrategy should
    # ever be using this (because RNN-strats should just be
    # operating on the bare vector)
    def parse_gamestate(self, vector, number):
        return {
            'supply': vector[:number],
            'deck_1': self._unvectorize(vector[number:number * 2]),
            'hand_1': self._unvectorize(vector[number * 2:number * 3]),
            'play_1': self._unvectorize(vector[number * 3:number * 4]),
            'bought_so_far_this_turn': self._unvectorize(vector[-(number + 2):-2]),
            'phase': vector[-2],
            'situation': vector[-1]}

    # Reads a vector of length equal to number of cards,
    # wherein the i-th value is how many of the i-th card
    # are in the subset,
    # and outputs a vector representing the subset
    #
    # e.g. [0, 3, 1, 2, 0, 0, 1, 0, 1, 0, ...] => [1,2,1,6,8,3,1,3]
    @staticmethod
    def _unvectorize(vector):
        response = []
        for index in range(len(vector)):
            response += [index] * vector[index]
        return response

    def _determine_actions_remaining(self, gamestate):
        remaining = 1
        for action_played_index in gamestate['play_1']:
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

    def _determine_buys_remaining(self, gamestate):
        remaining = 1
        for card_played_index in gamestate['play_1']:
            card = self.cards[card_played_index]
            if card['type'] == 'action' and 'buys' in card['action']:
                remaining += card['action']['buys']
        return remaining - len(gamestate['bought_so_far_this_turn'])

    def _determine_coins_available(self, gamestate):
        available = 0
        for index_played in gamestate['play_1']:
            card = self.cards[index_played]
            if card['type'] == 'treasure':
                available += card['value']
                continue
            if card['type'] == 'action' and 'coins' in card['action']:
                available += card['action']['coins']
        return available

    def _determine_spent_so_far_this_turn(self, gamestate):
        return sum(self.cards[index]['cost'] for index in gamestate['bought_so_far_this_turn'])

    def _pick_affordable_buy_targets(self, coins, gamestate):
        return [index for index in range(len(gamestate['supply'])) if
                gamestate['supply'][index] > 0 and self.cards[index]['cost'] <= coins]
