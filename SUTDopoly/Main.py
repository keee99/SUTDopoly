''' 
Computational Thinking and Design 1D project
F02 Group 02
Koh Jia Jun
Tan Kang Min
Chen Qinyi
Emmanuel J Lopez
'''


# Game Creation Dependencies
import traceback

# Essential Game Dependencies
import os
import random
import TurnFunctions
import GameInit
import Graphics
from GameInit import db, user, chance, community_chest
from time import sleep
from libdw import pyrebase



# This portion was modified from
# the code found at the following link:
# https://stackoverflow.com/questions/2084508/clear-terminal-in-python
if os.name == 'nt':
	clear = 'cls'
else:
	clear = 'clear'

def upload_firebase(use_firebase, string = None, cmd = None):
	if use_firebase:
		if cmd != None:
			db.child('cmd').set(cmd, user['idToken'])
		if string != None:
			db.child('string').set(string, user['idToken'])


# To run everytime the option "View the board" is pressed.
def PrintBoard(board, player):
	print('\nYour balance is: $' + str(player.money))
	print('\nNum |Name' + ' ' * 19 + '|Price |Rent  |Group          |Houses |Owner' + ' ' * 22 )
	for ind, prop in enumerate(board):
		print('{:<4}|{:<23}|{:<6}|{:<6}|{:<15}|{:<7}|{:<27}'.format(\
			ind, prop.titleName, prop.buyPrice, prop.rent, prop.color, prop.numHouse, prop.owner.name))
	print('\n')



# Executed during a Player's turn. Returns True/False to break game loop if someone wins. Runs within the main loop.
def turn(player, board, player_ind, use_firebase, Bank, player_names):

	# Update housesAvailable
	if use_firebase:
		housesAvailable = db.child('houses').get(user['idToken']).val()

	# Clears the screen everytime you take a new turn
	sleep(0.5)
	# Turn notification
	turn_string = "Its {0}'s turn! {0} has ${1}".format(player.name, player.money)
	upload_firebase(use_firebase, turn_string)
	print(turn_string)

	# Print current player location
	print('You are currently at {}.'.format(board[player.position].titleName))	

	# - Option to view board
	action = input('Roll Dice [Enter] / View Board [B] / View your Properties [V]\n').upper().strip()

	# Either option B and V, invalid option will just loop the thing.
	while action != '':
		if action == 'B':
			PrintBoard(board, player)

		# Unlike the PrintBoard function (line 40) this one prints only YOUR properties, and gives rent and house info as well.
		elif action == 'V':
			execViewProperties(player)

		action = input('Roll Dice [Enter] / View Board [B] / View your Properties [V]\n').upper().strip()


	# Roll dice 
	dice_1 = random.randint(1, 6)
	dice_2 = random.randint(1, 6)
	dice_roll = dice_1 + dice_2

	move_str = 'You rolled {}...'.format(dice_roll)

	# Runs the board movement as well as the board mvt animation. Check out move_board function is TurnFunctions.py
	pos, pos_ind, pos_string = TurnFunctions.move_board(player,dice_roll,board, move_str)
	print(pos_string + '\n')
	upload_firebase(use_firebase, pos_string)


	# TILE ACTIONS:
	# Special tile
	if pos.color == '-':
		execSpecialTile(player, player_ind, pos, use_firebase)

	# Unowned space
	elif pos.owner.name == 'Bank':
		execUnowned(player, player_ind, pos, pos_ind, board, use_firebase)


# 	Owned space: Collect rent.
	else:
		execOwned(player, player_ind, pos, use_firebase, player_names)


	# Post movement: Ask for command
	action = input('End Turn [Enter] / Build/Sell Houses [H] / Trade [T] / Mortgage [M] / View Board [V]').upper().strip()


	while action != '':
		
		# Build Houses
		if action == 'H':
			if player.properties:
				print()
				for i in range(len(player.properties)):
					print(f"{player.properties[i].titleName} [{i+1}]")
				propIndex = int(input("Choose a property [Give number] ")) - 1
				if propIndex in range(len(player.properties)):
					buyOrSell = input("Do you want to buy or sell [B/S] ").upper().strip()
					if TurnFunctions.count_properties(player, list(filter(lambda x: TurnFunctions.checkColor(x, player.properties[propIndex]), board)))[1]:
						if buyOrSell == "B":
							if housesAvailable > 0:
								if TurnFunctions.evenBuild(list(filter(lambda x: TurnFunctions.checkColor(x, player.properties[propIndex]), board)), player.properties[propIndex], 1):
									prop = player.properties[propIndex]
									if prop.numHouse < 4:
										prop.BuyHouse()
										housesAvailable -= 1
										# Firebase
										string, cmd = TurnFunctions.firebase_house(player, player_ind, buyOrSell, propIndex, prop)
										upload_firebase(use_firebase, string, cmd)

										print(f"You now have {prop.numHouse} house(s) on {prop.titleName}")
										print(f"Your new balance is ${player.money}")

									elif prop.numHouse == 4:
										prop.BuyHouse()
										housesAvailable += 4
										# Firebase
										string, cmd = TurnFunctions.firebase_house(player, player_ind, buyOrSell, propIndex, prop, "Hotel")
										upload_firebase(use_firebase, string, cmd)

										print(f"You now have a hotel on {prop.titleName}")
										print(f"Your new balance is ${player.money}")
									else:
										print(f"You already have a Hotel on {prop.titleName}")
								else:
									print(f"You must build houses on the other properties first before you can build on {player.properties[propIndex].titleName}")

								
						elif buyOrSell == "S":
							prop = player.properties[propIndex]
							if prop.numHouse > 0:
								if prop.numHouse == 5:
									if housesAvailable >= 4:
										prop.SellHouse()
										# Firebase
										string, cmd = TurnFunctions.firebase_house(player, player_ind, buyOrSell, propIndex, prop, "Hotel")
										upload_firebase(use_firebase, string, cmd)

										housesAvailable -= 4
										print(f"You now have {prop.numHouse} house(s) on {prop.titleName}")
									else:
										hotelSell = input("Not enough houses left to sell your hotel. Do you want to sell to get the most houses possible [Y/N] ").upper().strip()
										if hotelSell == "Y":
											for i in range(4-housesAvailable):
												prop.SellHouse()
												# Firebase
												string, cmd = TurnFunctions.firebase_house(player, player_ind, buyOrSell, propIndex, prop)
												upload_firebase(use_firebase, string, cmd)

												print(f"You now have {prop.numHouse} house(s) on {prop.titleName}")
												print(f"Your new balance is ${player.money}")
								else:
									if TurnFunctions.evenBuild(list(filter(lambda x: TurnFunctions.checkColor(x, prop), board)), prop, -1):
										prop.SellHouse()
										# Firebase
										string, cmd = TurnFunctions.firebase_house(player, player_ind, buyOrSell, propIndex, prop)
										upload_firebase(use_firebase, string, cmd)

										print(f"You now have {prop.numHouse} house(s) on {prop.titleName}")
										print(f"Your new balance is ${player.money}")
										housesAvailable += 1
									else:
										print("You must sell evenly")
							else:
								print("You don't have any houses to sell")
					else:
						print("You don't have a Monopoly in that color")
				else:
					print("Invalid Number")
				pass
			else:
				print("You don't own any properties")


		# Trade with another player
		elif action == 'T':
			# Filter out the players who lost.
			player.SetPlayerList(player_list, lost_players)
			print()
			for i in range(len(player.otherPlayerList)):
				print(f"{player.otherPlayerList[i].name} [{i + 1}]")
			tradingPlayerNum = int(input("Choose a player to trade with [Give number] ")) - 1

			if tradingPlayerNum in range(len(player.otherPlayerList)):
				tradingPlayer = player.otherPlayerList[tradingPlayerNum]
				print()
				for i in range(len(player.properties)):
					print(f"{player.properties[i].titleName} [{i + 1}]")

				propOfferedNum = input("Which properties do you offer? [Give number w/ spaces inbetween] ").split()
				moneyOffered = input("How much money do you offer? [$] ").strip()
				if moneyOffered == '':
					moneyOffered = 0
				else:
					moneyOffered = int(moneyOffered)

				print()
				for i in range(len(tradingPlayer.properties)):
					print(f"{tradingPlayer.properties[i].titleName} [{i + 1}]")

				propRequestedNum = input("Which properties do you request? [Give number w/ spaces inbetween] ").split()
				moneyRequested = input("How much money do you request? [$] ").strip()
				if moneyRequested == '':
					moneyRequested = 0
				else:
					moneyRequested = int(moneyRequested)

				if moneyOffered <= player.money and moneyRequested <= tradingPlayer.money:
					offer = f"{tradingPlayer.name}, do you accept the trade [Y/N] "

					if use_firebase:
						offer = list(map(lambda propertyNum: player.properties[int(propertyNum)-1], propOfferedNum))
						reqst = list(map(lambda propertyNum: tradingPlayer.properties[int(propertyNum)-1], propRequestedNum))
						offer_string = '$' + str(moneyOffered) + ', ' + ', '.join([x.titleName for x in offer]) 
						request_string = '$' + str(moneyRequested) + ' ' + ', '.join([x.titleName for x in reqst]) 
						
						string = f"\n{player.name} wants to trade with {tradingPlayer.name}!!\n\nOffering {offer_string} in exchange for {request_string}."
						upload_firebase(use_firebase, string)
						tradingList = [tradingPlayer.name, string]
						db.child('trade').set(tradingList, user['idToken'])
						db.child('tradeReply').set(None, user['idToken'])
						print('Waiting for response from other player...', end = '')

						# Waiting for his reply
						while db.child('tradeReply').get(user['idToken']).val() == None:
							sleep(0.5)
							print('.', end = '')

						print('\n')
						# Other party sends back a tuple of their player_ind and the reply (Y/N)
						tradingPlayerInd, reply = db.child('tradeReply').get(user['idToken']).val()
						
						
						if reply.strip().upper() == 'Y':
							player.Trade(tradingPlayer, list(map(lambda propertyNum: player.properties[int(propertyNum)-1], propOfferedNum)), moneyRequested, list(map(lambda propertyNum: tradingPlayer.properties[int(propertyNum)-1], propRequestedNum)), moneyOffered)
							cmd = "player_list[{0}].Trade(player_list[{1}], list(map(lambda propertyNum: player_list[{0}].properties[int(propertyNum)-1],\
							 		{2})), {3}, list(map(lambda propertyNum: player_list[{1}].properties[int(propertyNum)-1], {4})), {5})"\
									.format(player_ind, tradingPlayerInd, propOfferedNum, moneyRequested, propRequestedNum, moneyOffered)
							string = '{0} successfully traded with {1}, and exchanged {2} for {3}.'.format(player.name, tradingPlayer.name, offer_string, request_string)
							upload_firebase(use_firebase, string, cmd)
							print(string)

						else:
							print('Trade declined.')

					else:
						accepted = input(offer).strip().upper()
						if accepted == "Y":
							player.Trade(tradingPlayer, list(map(lambda propertyNum: player.properties[int(propertyNum)-1], propOfferedNum)), moneyRequested, list(map(lambda propertyNum: tradingPlayer.properties[int(propertyNum)-1], propRequestedNum)), moneyOffered)
							print("Trade Successful")
							print(f"{player.name}'s balance is ${player.money}")
							print(f"{tradingPlayer.name}'s balance is ${tradingPlayer.money}")
						elif accepted == "N":
							print("Trade Declined")
						else:
							print('Error, invalid input, aborted.')
				else:
					print("One or more players has insufficient funds")
			else:
				print("Invalid Player Number")



		# Mortgage property
		elif action == 'M':
			if player.properties:
				print()
				for i in range(len(player.properties)):
					print(f"{player.properties[i].titleName} [{i + 1}]")
				propIndex = int(input("Choose a property [Give number] ")) - 1
				if propIndex in range(len(player.properties)):
					if player.properties[propIndex].numHouse == 0:

						string = False

						if not player.properties[propIndex].isMortgaged:
							player.Mortgage(player.properties[propIndex])

							cmd = 'player_list[{0}].Mortgage(player_list[{0}].properties[{1}])'.format(player_ind, propIndex)
							string = f"{player.name} has mortgaged {player.properties[propIndex].titleName}, remaining balance is ${player.money}"

							print(string)

						else:
							if player.money >= player.properties[propIndex].buyPrice * 0.55:
								player.UnMortgage(player.properties[propIndex])

								cmd = 'player_list[{0}].UnMortgage(player_list[{0}].properties[{1}])'.format(player_ind, propIndex)
								string = f"{player.name} has unmortgaged {player.properties[propIndex].titleName}, remaining balance is ${player.money}"

								print(string)
							else:
								print("You don't have enough money to unmortgage this property")

						if use_firebase:
							if string:
								upload_firebase(use_firebase, string, cmd)

					else:
						print("Sell your houses first")
				else:
					print("Invalid Number")
			else:
				print("You have no properties")


		elif action == 'V':
			PrintBoard(board, player)


		# Developer tool for demonstration of features
		elif action == 'CHEAT':
			cheat = TurnFunctions.cheatcode(player_ind, None, player_list, board)
			cmd = 'TurnFunctions.cheatcode({}, "{}", player_list, board)'.format(player_ind, cheat)
			string = None
			upload_firebase(use_firebase, string, cmd)

		action = input('End Turn [Enter] / Build/Sell Houses [H] / Trade [T] / Mortgage [M] / View Board [V]').upper().strip()
	print('_______________________')

	if use_firebase:
		db.child('houses').set(housesAvailable, user['idToken'])

	# To test victory conditions
	# player.money = 0

	sleep(0.5)


 



def main():
	try:
		# Main menu
		os.system(clear)
		# imports and prints the main menu logo HAHA
		print(Graphics.main_menu)
		intro = 'Welcome to SUTDopoly!'
		print(intro)
		start_game = input('Host Game [H] / Join Game [J] / Single Computer[Enter]').upper().strip()

		while start_game not in ['J', 'H', '']:
			start_game = input('Please type a valid input: "J" or press Enter').upper().strip()


		# Initializing Players -> player names (list), player_list (list of player objects), 
		# player_names (list of names), player_number (no. of players), and use_firebase (Bool)
		global player_list
		player_name, player_names, player_list, player_number, use_firebase = GameInit.player_init(start_game)
		# Initializing board (list of property objects) and Bank (player object)
		global Bank
		board, Bank = GameInit.board_init()



		#Other Variables
		# turn_number -> Whose turn determined by (turn % len(player_list))
		turn_number = 0 
		# List of players who have lost the game. Will be appended by returning turnfunction.win_lose
		global lost_players
		lost_players = []
		# For property enhancement
		global housesAvailable
		housesAvailable = 32
		#Initializes firebase variables for proper initial running
		if use_firebase:
			db.child('turn_number').set(turn_number, user['idToken'])
			db.child('cmd').set(None, user['idToken'])
			db.child('string').set(None, user['idToken'])
			db.child('houses').set(housesAvailable, user['idToken'])
			db.child('trade').set([False, False], user['idToken'])
		# Sets initial current player: the first turn dude.
		current_player = player_list[ turn_number % len(player_list) ]


		# Some kind of loading screen LOL
		# Also Displays Turn Order
		print('\nTurns are in order of joining: {}'.format(', '.join(player_names)))
		sleep(2)
		print('Proceeding to the game....')
		sleep(0.6)

		os.system(clear)




		#Main Loop: Terminates by turnfunctions.win_lose()
		while True:

			# Main loop for offline play. Much much easier.
			if not use_firebase:
				current_player = player_list[ turn_number % len(player_names) ]

				if current_player not in lost_players: 
					turn(current_player, board, turn_number % len(player_names), use_firebase, Bank, player_names)

				# Checks for any player that lost.
				lost_players = TurnFunctions.Win_Lose(player_list, current_player.name, lost_players, Bank)
				turn_number += 1

				sleep(0.5)

			# Main loop for online play. Pain in the butt.
			else:
				# News -> the actions of your opponents. Printed on screen while not your turn.
				news = None
				# Cmd -> the actions to be RUN by the other player's scripts. Check out python's eval()/exec() functions
				# Cmd set as value to prevent actions from happening twice. Was a bug in the game.
				cmd = db.child('cmd').get(user['idToken']).val()

				# While not your turn: Check if its your turn.
				while current_player.name != player_name:

					# Constantly checks CMD and news 
					check_news = db.child('string').get(user['idToken']).val()
					check_cmd = db.child('cmd').get(user['idToken']).val()
					check_trade, demands = db.child('trade').get(user['idToken']).val()


					# If new news string: print it out
					if check_news != news:
						news = check_news
						print(news)
					# If new cmd string: eval() it. 
					if check_cmd != cmd:
						cmd = check_cmd
						try:
							eval(cmd)
						except:
							traceback.print_exc()
							try:
								exec(cmd)
							except:
								traceback.print_exc()
								print('failed to run changes')
					# Requests for trade
					if check_trade == player_name:
						print('Trade offer for you!!')
						print(demands + '\nUseful property info:')
						PrintBoard(board, player_list[player_names.index(player_name)])

						reply = input('Accept? [Y/N]')
						while reply.strip().upper() not in ['Y', 'N']:
							reply = input('Enter valid input. [Y/N]')
						player_ind = player_names.index(player_name)
						replyList = [player_ind, reply]

						db.child('tradeReply').set(replyList, user['idToken'])
						db.child('trade').set([False, False], user['idToken'])


					# Checks for new news and cmd strings every 0.3 seconds
					sleep(0.3) 

					# Updates current_player for the purpose of the while loop.
					new_turn_number = db.child('turn_number').get(user['idToken']).val()
					if new_turn_number != turn_number:
						lost_players = TurnFunctions.Win_Lose(player_list, player_name, lost_players, Bank)
						turn_number = new_turn_number

					current_player = player_list[ turn_number % len(player_list) ]

				# Exits the while loop when its your turn: Runs your turn() function
				# turn(player, board, player_ind, use_firebase, Bank, player_names)
				if current_player not in lost_players:
					turn(current_player, board, turn_number % len(player_names), use_firebase, Bank, player_names)

				# Updates turn info and player info for the next overall loop
				turn_number += 1
				db.child('turn_number').set(turn_number, user['idToken'])
				current_player = player_list[ turn_number % len(player_list)]

				lost_players = TurnFunctions.Win_Lose(player_list, player_name, lost_players, Bank)
				print('Ending Turn...')
				sleep(1.5)


		# RMB to clear player list on firebase once game ends, for hosting side.
		
	except:
		# traceback.print_exc()
		pass




def execViewProperties(player):
	props = player.properties
	if props:
		print('Name' + ' ' * 19 + '|Rent    |Group           |House    ' + '|Mortgage Status' + ' ' * 2)
		for prop in props:
			print('{:<23}|{:<8}|{:<16}|{:<9}|{:<17}'.format(prop.titleName, prop.rent, prop.color, prop.numHouse, "Mortgaged" if prop.isMortgaged == True else "Not Mortgaged"))
	else:
		print('You have no properties')
	print('\n')


def execSpecialTile(player, player_ind, pos, use_firebase):
	print('You landed on ' + pos.titleName)
	card = False
	if 'Chance' in pos.titleName:
		if chance == []:
			print('Ran out of Chance cards...')
		else:
			card = random.choice(chance)
	elif 'Community' in pos.titleName:
		if community_chest == []:
			print('Ran out of Community Chest cards...')
		else:
			card = random.choice(community_chest)

	TurnFunctions.chance_card(card, player)
	
	plyr = 'player_list[{}]'.format(player_ind)
	cmd = 'TurnFunctions.chance_card({}, {})'.format(card, plyr)
	string = None
	upload_firebase(use_firebase, string, cmd)



def execUnowned(player, player_ind, pos, pos_ind, board, use_firebase):
	print('This fifth row is unowned! It costs ${} to run, and it is part of the {} group.'.format(pos.buyPrice, pos.color))
	print('You have ${}.\n'.format(player.money))
	
	action = input('Buy [B] / skip [Enter] / View Board [V]\n').upper().strip()

	if action == 'V':
		PrintBoard(board, player)
		action = input('\nBuy [B] / skip [Enter]\n').upper().strip()

	if action == 'B':
		# Trade function runs with the bank.
		Bank.Trade(player, [pos], pos.buyPrice)

		# FIrebase acrobatics
		cmd = "Bank.Trade(player_list[{0}], [board[{1}]], board[{1}].buyPrice)".format(player_ind, pos_ind)
		string = '{} bought {}! Remaining balance: ${}'.format(player.name, pos.titleName, player.money)
		upload_firebase(use_firebase, string, cmd)

		print('You bought {}. You now have ${} remaining.'.format(pos.titleName, player.money))

	else:
		print('You passed :((')



def execOwned(player, player_ind, pos, use_firebase, player_names):
	if pos.owner == player:
		print('Landed on your own property.')

	elif pos.isMortgaged == True:
		print('Mortgaged property: No rent collected.')

	else:
		print('Uh oh! The fifth row is owned!')
		sleep(1)
		print('Time to pay club fees!')
		sleep(0.5)

		# Local Changes
		player.money -= pos.rent
		pos.owner.money += pos.rent
		pos_owner_ind = player_names.index(pos.owner.name)
		string = "{0} paid ${2} to {3}. {0}'s remaining balance: ${1}, {3}'s balance: ${4}".format(\
						player.name, player.money, pos.rent, pos.owner.name, pos.owner.money)
		print(string)

		# Firebase acrobatics again -> Online changes
		cmd = "player_list[{2}].Trade(player_list[{0}], [], {1})".format(player_ind, pos.rent, pos_owner_ind)
		upload_firebase(use_firebase, string, cmd)



# Runs main() if the script executed directly is Main.py. Otherwise, eg if imported, this wont run.
if __name__ == '__main__':
	main()
