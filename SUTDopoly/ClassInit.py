''' 
Computational Thinking and Design 1D project
F02 Group 02
Koh Jia Jun
Tan Kang Min
Chen Qinyi
Emmanuel J Lopez
'''


class Player:
    def __init__(self, name): #properties is a list of owned
        self.money = 1500
        self.properties = []
        self.position = 0
        self.name = name
        self.otherPlayerList = []

    def SetPlayerList(self, allPlayerList, lostPlayerList = False):           #set for each player obj after creating all player obj
        self.otherPlayerList = allPlayerList[:]
        self.otherPlayerList.remove(self)
        if lostPlayerList:
            for p in lostPlayerList:
                try:
                    self.otherPlayerList.remove(p)
                except:
                    pass

    def CheckVictory(self, allPlayersList):
        gameState = True
        self.SetPlayerList(allPlayersList)

        for otherPlayer in self.otherPlayerList:
            if otherPlayer.money > 0:
                gameState = None

        if self.money <= 0:
            gameState = False
        return gameState

    def Trade(self, tradingPlayer, propertiesRequested=[], moneyOffered=0, propertiesOffered=[], moneyRequested=0):
        for propertyRequested in propertiesRequested:
            if propertyRequested in self.properties:
                propertyRequested.ChangeOwner(tradingPlayer)
                self.properties.remove(propertyRequested)
                tradingPlayer.properties.append(propertyRequested)

        for propertyOffered in propertiesOffered:
            if propertyOffered in tradingPlayer.properties:
                propertyOffered.ChangeOwner(self)
                self.properties.append(propertyOffered)
                tradingPlayer.properties.remove(propertyOffered)

        self.money += moneyOffered - moneyRequested
        tradingPlayer.money += moneyRequested - moneyOffered

    def OutOfJail(self, roll1, roll2, bail=False): #enter none for roll if paid bail
        if bail:
            self.money -= 250
            return True
        else:
            if roll1 == roll2:
                return True
            else:
                return False

    def Mortgage(self, prop):  # check for no houses before using
        self.money += int(prop.buyPrice * 0.5)
        prop.isMortgaged = True
        prop.rent = 0

    def UnMortgage(self, prop):
        self.money -= int(prop.buyPrice * 0.55)
        prop.isMortgaged = False
        prop.rent = prop.housedRent[0]


class Property:
    propertyColors = ["brown", "Cyan", "pink", "orange", "red", "yellow", "green", "dark blue"]

    def __init__(self, owner, titleName, buyPrice, housedRent, color, numHouse=0):  # housedRent is a tuple with {no:rent}, owner is Player object
        propertyColors = ["brown", "Cyan", "pink", "orange", "red", "yellow", "green", "dark blue"]
        self.titleName = titleName
        self.buyPrice = buyPrice
        self.numHouse = numHouse                                    # numHouse is the number of houses/ 6 houses = hotel
        self.isMortgaged = False
        self.color = color
        self.owner = owner
        self.housedRent = housedRent
        self.rent = housedRent[numHouse]

        for i in range(0, len(propertyColors)-1, 2):
            if self.color == propertyColors[i] or self.color == propertyColors[i+1]:
                self.housePrice = 50 * (i+1)

    def BuyHouse(self, numToBuy=1):
        self.numHouse += numToBuy
        self.owner.money -= self.housePrice * numToBuy
        self.rent = self.housedRent[self.numHouse]

    def SellHouse(self, numToSell=1):
        self.numHouse -= numToSell
        self.owner.money += self.housePrice * numToSell * 0.5
        self.rent = self.housedRent[self.numHouse]

    def ChangeOwner(self, newOwner):  # method to change owner of property --> trading
        self.owner = newOwner





