import gamestate
from deck import Deck


# Return value from most methods from Gamemaster
# is the new situation that the game is now in
# after execution.

class Gamemaster:
    def __init__(self, cards):
        self.cards = cards
        for index, card in enumerate(cards):
            if card['name'] == 'Copper':
                copper_index = index
                continue
            if card['name'] == 'Estate':
                estate_index = index

        if copper_index is None or estate_index is None:
            raise Exception('At least one of Copper or Estate was not found in `cards`')

        self.gamestate = self.build_initial_gamestate(copper_index, estate_index)

    def build_initial_gamestate(self, copper_index, estate_index):
        supply = self._make_supply()
        deck_1, deck_2 = self._make_decks(copper_index, estate_index)
        return gamestate.create_initial_gamestate(supply, deck_1, deck_2)

    def pretty_print_hand(self):
        return ','.join([self.cards[i]['name'] for i in self.gamestate.hand_1])

    def play_action(self, player_number, situation, index):
        if situation != 0:
            raise ValueError('Tried playing an action outside the Action Phase')

        card = self.cards[index]
        if card['type'] != 'action':
            raise ValueError(card['name'] + ' is not an action!')

        try:
            self.gamestate.play_card(player_number, index)
        except ValueError:
            raise ValueError('No ' + card['name'] + ' in hand!')

        # OK, we've physically moved the card into the play area - now to execute
        # whatever the card told us to do.
        # Right now, the only thing that is supported is drawing cards
        if 'cards' in card['action']:
            for i in range(card['action']['cards']):
                self.gamestate.player_draw(player_number)
        return situation  # Same situation

    def play_treasure(self, player_number, situation, index):
        if situation != 1:
            raise ValueError('Tried playing a treasure outside the Buy Phase')

        card = self.cards[index]
        if card['type'] != 'treasure':
            raise ValueError(card['name'] + ' is not a treasure!')

        try:
            self.gamestate.play_card(player_number, index)
        except ValueError:
            raise ValueError('No ' + card['name'] + ' in hand!')
        return situation  # Same phase

    def buy_card(self, player_number, situation, index):
        if situation != 1:
            raise ValueError('Tried playing a treasure outside the Buy Phase')

        self._check_legal_to_buy_card(player_number)

        total_cost = sum([self.cards[index]['cost'] for index in self.gamestate.bought_so_far_this_turn + [index]])
        total_coins = self._get_total_coins(player_number)
        if total_cost > total_coins:
            raise ValueError('Cannot afford that!')

        try:
            self.gamestate.buy_card(player_number, index)
            return situation  # Same phase
        except ValueError:
            raise ValueError('No ' + self.cards['name'] + ' left in supply!')

    # player_number is required as part of the "interface" of game actions,
    # even though it's not needed in this specific action
    def end_phase(self, player_number, situation, verbose=False):
        if situation not in range(3):
            raise ValueError('Cannot end phase in a special situation!')
        current_phase = self.gamestate.phase
        next_phase = self.gamestate.get_next_phase()
        self.gamestate.phase = next_phase
        if verbose:
            print('You just ended the ' + current_phase + ' phase and are now in the ' + next_phase + ' phase')
        if self.gamestate.phase.startswith('cleanup'):
            # TODO - for cards that trigger on discarding, this will need to execute some logic
            self.gamestate.cleanup(int(self.gamestate.phase[-1]))
            if verbose:
                print('Cleaned up')
        return (situation + 1) % 3

    def determine_scores(self):
        player_1_score = sum([self.cards[index]['points'] if self.cards[index]['type'] == 'victory' else 0 for index in
                              self.gamestate.deck_1.contents() + self.gamestate.hand_1 + self.gamestate.discard_1])
        player_2_score = sum([self.cards[index]['points'] if self.cards[index]['type'] == 'victory' else 0 for index in
                              self.gamestate.deck_2.contents() + self.gamestate.hand_2 + self.gamestate.discard_2])
        return player_1_score, player_2_score

    def _make_supply(self, number_of_players=2):
        supply = []
        for card in self.cards:
            if card['name'] == 'Copper':
                supply.append(60 - (7 * number_of_players))
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

    @staticmethod
    def _make_decks(copper_index, estate_index, number_of_decks=2):
        response = []
        for i in range(number_of_decks):
            response.append(Deck([copper_index] * 7 + [estate_index] * 3))
        return response

    def _check_legal_to_buy_card(self, player_number):
        cards_played = [self.cards[index] for index in getattr(self.gamestate, 'play_' + str(player_number))]
        extra_buys = sum(
            [card['action']['buys'] for card in cards_played if card['type'] == 'action' and 'buys' in card['action']])
        if extra_buys < len(
                self.gamestate.bought_so_far_this_turn):  # strict equality because you always start with one buy
            raise ValueError("Trying to buy too many cards in one turn")

    def _get_total_coins(self, player_number):
        total_coins = 0
        for index in getattr(self.gamestate, 'play_' + str(player_number)):
            card = self.cards[index]
            if card['type'] == 'treasure':
                total_coins += card['value']
                continue
            if card['type'] == 'action' and 'coins' in card['action']:
                total_coins += card['action']['coins']
        return total_coins
