#!python3 -i
from cards import cards
from gamemaster import Gamemaster
from strategies.randomStrategy import RandomStrategy

GM = Gamemaster(cards)


strat = RandomStrategy(cards, 1)


def what():
    return strat.determine_action(GM.gamestate)


def ok():
    getattr(GM, _[0])(*_[1])  # ...holy shit.


def skip():
    while GM.gamestate.phase != 'action_1':
        GM.end_phase()


def state():
    print(GM.gamestate)
