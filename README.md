# Minesweeper with AI
My attempt at recreating the classic Minesweeper with a twist! This one includes a built-in AI.
### Running 
* If you just want to run the game
``` shell
cd Game
python Engine.py
```

* If you want to tweak board's settings

``` python3
# Board.py
BOARD_WIDTH_S  = 30
BOARD_HEIGHT_S = 16
BOARD_MINES_S  = 99
```
* If you want to turn off the AI

``` python3
# Board.py
"""
            _    ___        ____ _____ _   _ _____ _____
           / \  |_ _|      / ___|_   _| | | |  ___|  ___|
          / _ \  | |       \___ \ | | | | | | |_  | |_
         / ___ \ | |        ___) || | | |_| |  _| |  _|
        /_/   \_\___|      |____/ |_|  \___/|_|   |_|
"""

# Use AI?
USE_AI: bool = False
```

* If you want see the AI run as fast as possible
```
# Board.py
"""
            _    ___        ____ _____ _   _ _____ _____
           / \  |_ _|      / ___|_   _| | | |  ___|  ___|
          / _ \  | |       \___ \ | | | | | | |_  | |_
         / ___ \ | |        ___) || | | |_| |  _| |  _|
        /_/   \_\___|      |____/ |_|  \___/|_|   |_|
"""

# Use AI?
ai_delay: int = 0
```




## Authors

* **Resting Kiwi** - *Everything* - [RestingKiwi](https://github.com/PurpleBooth)



## Acknowledgments

* Shout out to [nguyenpanda](https://github.com/nguyenpanda) for helping me fix a bug that causes the Pygame window not displaying on MacOS.
