# Fantom board game

This is a Python implementation of a popular board game [Fantom](https://www.ihrysko.sk/fantom-p13134) (or [Scotland Yard](https://boardgamegeek.com/boardgame/438/scotland-yard)) with the map redesigned and adapted to the streets of Bratislava, Slovakia.

The game is started by:

```python
python fantom.py
```

The game is controlled either by clicking on the circles or on the vehicle icons.

The point of the game is that one player, playing as the Fantom, moves secretly across the map, while five agents try to find the Fantom.

To move across the map, players use transportation methods, and each agent has a limited number of tickets for these transportation methods. The Fantom receives the used tickets of the agents. The transportation methods are: bus (black), tram (green), and taxi (red). The Fantom also has two special types of tickets: boat (blue) and a double move, which allows the Fantom to make two moves in a row.

Movement by a specific transportation method between two circles is only allowed if those circles are stops for that method—indicated by coloring the circle with the corresponding color (excluding the boat, whose stops are marked with blue lines). Additionally, there must be a route marked on the map in that color between the two circles, and the route must not pass through another stop for the same transportation method.

The Fantom’s position is revealed five times during the game, and the specific rounds in which this happens are set in the game.

The game ends with a victory for the agents if one of them lands on the same circle as the Fantom at the same time. The Fantom wins if they complete 24 rounds without being caught by any agent.
