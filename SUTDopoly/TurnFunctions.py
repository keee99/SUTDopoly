''' 
Computational Thinking and Design 1D project
F02 Group 02
Koh Jia Jun
Tan Kang Min
Chen Qinyi
Emmanuel J Lopez
'''


import Graphics
from time import sleep

	
def count_properties(player_object, color_group_list):
    
    counter = 0
    
    for i in range(len(color_group_list)):
        if (color_group_list[i] in player_object.properties):
            counter += 1
    
    return counter, counter == len(color_group_list)


def checkColor(property, playerProp):
    if property.color == playerProp.color:
        return property


def evenBuild(color_group_list, currrentProp, bs):
    houses = []
    for i in color_group_list:
        houses.append(i.numHouse)
    houses[houses.index(currrentProp.numHouse)] = currrentProp.numHouse + bs
    if max(houses) - min(houses) <= 1:
        return True
    else:
        return False


def firebase_house(player, player_ind, buysell, propIndex, prop, houseOrHotel = 'house', n = ''):
	player_str = 'player_list[{}]'.format(player_ind)

	if buysell == 'B':
		cmd = '{0}.properties[{1}].BuyHouse({2})'.format(player_str, propIndex, str(n))
		string = '{0} bought a {3} for the property {1}! It has now {2} houses.'.format(player.name, prop.titleName, prop.numHouse, houseOrHotel)

	if buysell == 'S':
		cmd = '{0}.properties[{1}].SellHouse({2})'.format(player_str, propIndex, str(n))
		string = '{0} sold a {3} from the property {1}! It has now {2} houses.'.format(player.name, prop.titleName, prop.numHouse, houseOrHotel)

	return string, cmd


def Win_Lose(player_list, player_name, false_players, Bank):
	for player_object in player_list:
		win_bool = player_object.CheckVictory(player_list)
		if win_bool == False and (player_object not in false_players):
			print('-'*50 + '\n{} is bankrupt and is out of the game!!\n'.format(player_object.name) + '-'*50)
			sleep(1)
			for property in player_object.properties:
				player_object.Trade(Bank, [property])
			false_players.append(player_object)
	if (len(player_list) - len(false_players)) == 1:
		winner = None
		for x in player_list:
			if x not in false_players:
				winner = x
				break	
		if winner.name == player_name:
			Graphics.PrintWin()
		else:
			Graphics.PrintLose()
		print(winner.name.upper() + ' WINS THE GAME!!!')
		print('\n Press enter to exit the game. Thanks for playing!')
		input()
		exit()

	return false_players


def check_go(initial_pos, final_pos, player_object, board):
    
    if final_pos >= len(board):
        print(Graphics.go)
        player_object.money += 200
        print( player_object.name + ' passed GO! Collect 200 dollars!')


def move_board(player, dice_roll, board, move_str):
	initial_pos, final_pos = player.position, player.position + dice_roll

	Graphics.Board_Animation(board, initial_pos, final_pos, move_str)

	final_board_index = final_pos % len(board) 
	player.position = final_board_index
	pos = board[final_board_index]

	check_go(initial_pos, final_pos, player, board)	
	
	return (pos, final_board_index, '{} moved {} steps to {}!!'.format(player.name, dice_roll, pos.titleName) )


def chance_card(card, player):
	if bool(card) == True:
		print(card[0])
		player.money += card[1]
		print('{} has ${} remaining.'.format(player.name, player.money))



def cheatcode(player_ind, cheat, player_list, board):
	if cheat == None:
		cheat = input('?\n').upper().strip()

	flag = False

	# Make every other player bankrupt instantly
	if cheat == 'WIN':
		flag = True
		for x in range(len(player_list)):
			if x == player_ind:
				continue
			player_list[x].money = 0

	# Make yourself bankrupt instantly
	elif cheat == 'LOSE':
		flag = True
		player_list[player_ind].money = 0

	# Makes you rich 
	elif cheat == 'GODMODE':
		flag = True
		player = player_list[player_ind]
		player.money += 10000000
		for prop in board:
			if prop.color != '-':
				prop.numHouse = 5
				prop.owner = player
				player.properties.append(prop)

	if flag:
		print('CHEAT CODE ACTIVATED')

	return cheat
