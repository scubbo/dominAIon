#!python3 -i
from cards import cards
from gamemaster import Gamemaster
GM = Gamemaster(cards)

import sys
sys.path.append('strategies')
from randomStrategy import RandomStrategy
strat = RandomStrategy(cards)

def what():
  return strat.determine_action(GM.gamestate)

def ok():
  getattr(GM, _[0])(*_[1]) #...holy shit.

def skip():
  while GM.gamestate.phase != 'action_1':
    GM.end_phase()