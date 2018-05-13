==Overview==

Uses ML to train strategies to play Dominion.

==Class Overview==

The Gamerunner is responsible for running the game. It:
* Handles filesystem interactions for persisting moves and W/L.
* Queries the Gamestate for a GamestateView, and passes that to the relevant Strategy.
* Receives a move-selection vector from the Strategy, and, for each proposed move in descending order of selection-strength:
 * Translates the move into a command to Gamemaster
 * Executes the command on the Gamemaster
 * If the move was illegal (i.e. if the Gamemaster throws an Exception), record the move as illegal and try again with the next-most-strongly-selected move
  * (Note that there is no need for a termination condition, because there is always a legal move - usually, "end the phase")
 * If the move was legal, record it, then loop again (query Gamestate for a GamestateView, pass to stragety, etc.)
* Detects when the game should end, totals the scores, and determines the winner.

The Gamemaster is responsible for checking move legality against game rules, and executing legal moves.

The Gamestate tracks the state of the game. It is also responsible for providing "views" onto the Gamestate, depending on the situation. For instance, a player should never know what is in the opponent's hand, nor the exact order of their deck. Additionally, in some situations (like during the resolution of some Action cards), cards are in unusual zones (such as "revealed but not in hand" or "drawn - but need to be tracked for possible immediate discard"), so the Gamestate should represent those as differently formed vectors.

A GamestateView (not a separate class! But an important-enough concept that it warrants its own name) is a tuple of `(situation, [state_vector])`. `situation` is an integer representing the situation in which the Strategy is being asked to make a decision - for instance, "during the Buy Phase", "during resolution of a Harbinger", "in response to the opponent playing an Attack card". `[state_vector]` encodes the state at that point in time. These will *usually* be of a standard form (since most decisions will be being made during the two most common situations - "your Buy phase" or "your Action phase"), but may sometimes have extra elements (to represent the "unusual zones" described above). This implies that the RNN's that a Strategy encompasses for each situation will (potentially) have differently-sized input vectors.

A Strategy, when given a GamestateView, returns a vector representing the selection-strength of each possible action. This is an intentional choice (as opposed to the Strategy being responsible for determining the single selected action) since it allows the Gamerunner to "try" decreasingly strongly-selected options if some strongly-selected ones are illegal.

A Situation is defined in configuration that is loaded at initialization. A Situation configuration includes:
* A human-readable definition of the Situation (useful for debugging and human parsing!)
* Definition (human-readable? Automated? TBD. Automated would be smoothest and prevent code duplication that could potentially get out-of-sync, but we'll see how hard that is to do...) of how to translate from GamestateView to input-vector (for Gamestate), and from output-vector to moves (for Gamerunner to translate and then pass to Gamemaster).