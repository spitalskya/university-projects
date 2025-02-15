# Azul board game

**Team:**  
Andrej Spitalsky, Tomas Antal, Erik Bozik, Teo Pazera, Rafael Rohal  

- This is a Python implementation of the board game Azul, designed to be played in the terminal.  
- The team collaborated on some components of the project, which can be found in the repository: [PTS1-Azul](https://github.com/spitalskya/PTS1-Azul).  

## Interacting with the Game  

- The game is initialized by running the `make game` command.  
- To start a game, use the `start` command followed by the number of players (`int`) and a unique ID (`int`) for each player.  
- Moves are performed using the `take` command, followed by four integers:  
  - `player_id` – ID of the player taking the turn  
  - `source_idx` – Index of the tile source from which tiles are taken  
  - `idx` – Index of the tile the player wishes to take  
  - `destination_idx` – Pattern line where the player places the taken tiles  
- The game session can be terminated at any time using the `end` command.  

## Example game session

```shell
make game
start 3 10 11 12
take 10 1 2 2
take 11 5 1 1
take 12 2 1 1
take 10 0 4 1
end
```

- board state after example moves

```shell
▼▼▼▼▼▼▼▼▼▼
Player to take: 11
Take command structure: take [player ID] [tile source] [tile code] [pattern line]

Tile codes: |0: L| |1: B| |2: G| |3: R| |4: Y|

Table center: |0: BR|
Factories: |1: | |2: | |3: BGLY| |4: BGGR| |5: | |6: BBGL| |7: LLRY|

|---------------|       |---------------|       |---------------|
|Board of 10    |       |Board of 11    |       |Board of 12    |
|Points: 0      |       |Points: 0      |       |Points: 0      |
|0 :    _ byrlg |       |0 :    _ byrlg |       |0 :    _ byrlg |
|1 :   YY gbyrl |       |1 :   BB gbyrl |       |1 :   BB gbyrl |
|2 :  GGG lgbyr |       |2 :  ___ lgbyr |       |2 :  ___ lgbyr |
|3 : ____ rlgby |       |3 : ____ rlgby |       |3 : ____ rlgby |
|4 :_____ yrlgb |       |4 :_____ yrlgb |       |4 :_____ yrlgb |
|Floor: SY      |       |Floor:         |       |Floor:         |
|---------------|       |---------------|       |---------------|

Bag: |B: 11| |G: 13| |L: 16| |R: 17| |Y: 15|
Used tiles:
▲▲▲▲▲▲▲▲▲▲
```
