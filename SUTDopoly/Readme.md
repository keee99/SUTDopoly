Do note that the current iteration of the application does NOT support online play, as the firebase realtime DB instance has been taken down.

1. Run these installations:

    pip install libdw

2. To start the game, make sure each file is present in the same directory:

        ClassInit.py
        GameInit.py
        Graphics.py
        Main.py
        TurnFunctions.py
        __init__.py


3. To start, navigate to the directory using a terminal, and run Main.py.

    python Main.py

For online play, run Main.py in the same fashion on multiple terminals or computers. (Legacy)
To start an online game, a player must first host a game by entering 'H' on the main menu, only following which other players can join by entering 'J'.
No 2 players in an online game can have the same name.
