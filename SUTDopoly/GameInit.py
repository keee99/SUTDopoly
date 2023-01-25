''' 
Computational Thinking and Design 1D project
F02 Group 02
Koh Jia Jun
Tan Kang Min
Chen Qinyi
Emmanuel J Lopez
'''


import ClassInit
from time import sleep
from libdw import pyrebase

db = None
user = None

# Initializes Players. Returns player_list (list of player objects), player_names (list of names), 
#player_number (no. of players), and use_firebase (wether or not we're using online play)
def player_init(start_game): 
	# User chooses to play on one computer
	if start_game == '':
		use_firebase = False
		player_name = False # Playing locally: No single local player.

		# Choosing number of players: gives 2 to 8 players, as a STRING to be converted right after this lol
		player_number = input('Number of Players? (Min 2, Integer Value) ').strip()
		while (not player_number.isdigit()) or (2 > int(player_number)):

			if not player_number.isdigit():
				player_number = input('Please type an integer value.')
			elif int(player_number) < 2:
				player_number = input('More players please! (Min 2) ')

		
		# Initializing for data collection
		player_names = [] 	# List of strings representing player names
		player_list = [] 	# List of player objects, in same order as player names. Dictionary not used because we want ordered dataset.
		player_number = int(player_number)

		# Collecting Player Names
		for n in range(player_number):
			name = input('Name of player {}? '.format(n + 1)) # Name of player 1? is the first print.
			while name in player_names: # While loop prevents repetition of names.
				name = input('Name already taken! Please input another name: ') 

			# Initializing player objects and appending to player_list and player_names
			player_names.append(name)
			player_list.append(ClassInit.Player(name))

	
	else: # Online play

		# Firebase Initialization
		# This portion was modified from
		# the code found in 10.014 Lab Files,
		# at the following link:
		# https://drive.google.com/drive/folders/1Dxae5fcGRc4d6eGHAOHmMW0r1vtGKnUV


		try:
			dbid = "FIREBASE-DB-ID"
			url = "https://" + dbid + ".firebaseio.com"
			auth_domain = dbid + ".firebaseapp.com"
			api_key = "SECRET"
			mail = "MAIL@MAIL.com"
			pwd = "SECRET" 

			config = {"apiKey": api_key, "authDomain": auth_domain, "databaseURL": url}
			fb = pyrebase.initialize_app(config)
			auth = fb.auth()
			user = auth.sign_in_with_email_and_password(mail, pwd)
			db = fb.database()
			user = auth.refresh(user['refreshToken']) 

		except:
			print("Online Play unavailable.")
			sleep(1)
			print("Reverting to offline play.")
			sleep(1)
			return player_init("")


		player_name = input('Please input your name.')
		use_firebase = True
		key = 'players'

		# User to Host Game
		if start_game == 'H':

			# Initializing firebase values to host new game.
			db.child(key).set([player_name], user['idToken']) #key = players -> accesses a list of player names 
			db.child('started').set('False', user['idToken']) #started -> accesses whether or not the game has started.

			print('\nPress [Enter] to refresh the player list. Type START once every player has joined the room. Make sure there are at least 2 players!')
			while True:
				command = input()
				player_list = db.child(key).get(user['idToken']).val()
				if command.strip().lower() == 'start' and (2<= len(player_list) <= 8):
					db.child('started').set('True', user['idToken'])
					break
				print('Number of Players:', len(player_list), end = '\n')


		# User to Join Game
		elif start_game == 'J':

			# If game has started, exits.
			if db.child('started').get(user['idToken']).val() == 'True':
				print('Room is in session!! Host a new game instead!')
				input('Press enter to exit')
				exit()

			players = db.child(key).get(user['idToken']).val()

			if players == None: # If joining empty room: exits
				print('No players in room. Please host a new game instead.')
				input('Press enter to exit')
				exit()

			else: # Joining non-empty room
				print('Joining Game.\n')
				db.child(key).set(players + [player_name], user['idToken'])

			# Joining until host
			print('Waiting for host to start game...')
			while db.child('started').get(user['idToken']).val() != 'True':
				sleep(1) # Prevent spamming of API.


		# Done on all users so that player_list is accessible thruout
		player_names = db.child('players').get(user['idToken']).val()	# List of strings representing player names
		player_list = [ClassInit.Player(n) for n in player_names]  	# List of player objects, in same order as player names. Dictionary not used because we want ordered dataset.
		player_number =	len(player_list)	


	for plr in player_list:
		plr.SetPlayerList(player_list) # Complete the initialization for the player object. See ClassInit documentation

	return player_name, player_names, player_list, player_number, use_firebase


def board_init():
	# Init Board
	board = []
	Bank = ClassInit.Player("Bank")
	Bank.money = 10000000000
	titleDeedData = { # buyPrice, housedRent, color
		"GO":  ('-', (0,), '-'),

	    "Judo": (60, (2,10,30,90,160,250), "brown"), 
	    "Muay Thai": (60, (4,20,60,180,320,450), "brown"),

	    "Chance!":  ('-', (0,), '-'),						#chance
	 
	    "SOAR": (100, (6,30,90,270,400,550), "Cyan"), 
	    "Design Odyssey": (100, (6,30,90,270,400,550), "Cyan"), 
	    "3DC Developer": (120, (8,40,100,300,450,600), "Cyan"), 

	 	"Community Chest!":  ('-', (0,), '-'),						#chance

	    "SUTD Chamber": (140, (10,50,150,450,625,750), "pink"), 
	    "SUTD Bands": (140, (10,50,150,450,625,750), "pink"), 
	    "SUTDio": (160, (12,60,180,500,700,900), "pink"),

	    "Community Chest!!":  ('-', (0,), '-'),						#chance
	 	
	    "Production": (180, (14,70,200,550,750,950), "orange"), 
	    "ROOT": (180, (14,70,200,550,750,950), "orange"), 
	    "Minions": (200, (16,80,220,600,800,1000), "orange"),

	    "Vacation!":  ('-', (0,), '-'),
	 
	    "DDZ": (220, (18,90,250,700,875,1050), "red"), 
	    "FUNKtion": (220, (18,90,250,700,875,1050), "red"), 
	    "Ballroom Dancing": (240, (20,100,300,750,925,1100), "red"),

	    "Chance!!":  ('-', (0,), '-'),						#chance 
	 
	    "APEX": (260, (22,110,330,800,975,1150), "yellow"), 
	    "Floorball": (260, (22,110,330,800,975,1150), "yellow"), 
	    "Badminton": (280, (24,120,360,850,1025,1200), "yellow"),

	    "Bootcamp":  ('-', (0,), '-'),
	 
	    "Archery": (300, (26,130,390,900,1100,1275), "green"), 
	    "Cheer": (300, (26,130,390,900,1100,1275), "green"), 
	    "Grub Club": (320, (28,150,450,1000,1200,1400), "green"), 

	    "Chance!!!":  ('-', (0,), '-'),						#chance
	 
	    "Muslim Community": (350, (35,175,500,1100,1300,1500), "dark blue"), 
	    "Taal Indian Dance Club": (400, (50,200,600,1400,1700,2000), "dark blue") 
	} 

	for titleName, data in titleDeedData.items():
		prop = ClassInit.Property(Bank, titleName, data[0], data[1], data[2])
		board.append(prop)
		Bank.properties.append(prop)

	return board, Bank



chance= [
("Burnt too much midnight oil and overslept! Pay a late fee of $20",-20),
("Pay tuition fees of $200 to the bank",-200),
("You got a scholarship! Congratulations, collect $500 from the bank",500),
("You are too close from your friend. Tsk, safe distancing! You got fined $100",-100),
("You picked up a wallet from the ground and returned it to its' grateful owner. He gifts you $20",20),
("Buried treasure is discovered. Collect $150",150),
("Oops, you left some important and urgent work at home. Bribe your sibling $50 at home help you out",50),
("Clerical error in tuition fees, congrats, you got refunded $50 from the bank",50),
("You found a way to bypass Pick&Go's scanner. Get $50 from the bank",50),
("You got food poisoning from Mixed Rice's stall. Oh dear, pay $60 in hospital fees",-60),
("Your group just won a coding competition. Congrats, collect $50 from the bank. Laugh at the rest along the way there",50),
("Pay hostel fees of $100",-100),
("Collect $200 of pocket money. You love your parents, especially when you are a penniless uni student",200),
("You can go for an overseas exchange programme. Pay the bank $200 worth of airplane and expenses costs",-200),
("You just got a girlfriend/boyfriend who insists you pay for every date. Give the bank $50",-50),
("You just got a girlfriend/boyfriend who insists they pay for every date. Receive $50 from the bank",50)
]

community_chest= [
("Pay tuition fees of $200 to the bank",200),
("You got a scholarship! Congrats, take $1000 from the bank", 1000),
("The bank forgot to collect money from you. Give $50 back to the bank",-50),
("You forgot the time and was late for your fifth row. Pay a late fee of $20", -20),
("Uh oh! You forgot that an exam is today. Pay $50 to reflect on your time management skills (or lack thereof)", -50),
("You got caught copying a friend's homework. Tsk tsk. Pay the bank $200",-200),
("Collect $20 from the bank. You found someone's money on the ground",20),
("Your fifth row is collecting funds. Again. Pay the bank $20",-20),
("Your class is playing Angels and Mortals. Collect some material happiness of $20 from the bank",20),
("Your class is playing Angels and Mortals. Give some material happiness of $20 to the bank. Your mortal thanks you.",-20),
("You play the ' has a bright future with lots of potential' card. Get $300 from the bank",300),
("You got caught selling your homework answers. Pay $300 to the bank",-300),
("You sell your homework to the desperate. Receive $200 from the bank",200),
("Collect $10 from the bank. Congrats, you won a prize for participating in a poll",10),
("Your hostel room got infested with cockroaches. Pay $50 for an exterminator", -50),
("You forgot to close the hostel windows during the window washing. Pay $50 to fix your water-logged computer",-50),
("You hate your roommate. Pay $50 for daily transport fees to avoid seeing your roommate's face",-50),
("Pay poor tax of $20",-20),
("Clerical error. The bank pays you $200",200),
("Your roommate hates you. He pays you $50 to bribe you from staying in the same room as him",50)
]

