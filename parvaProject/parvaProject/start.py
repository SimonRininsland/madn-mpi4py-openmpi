from parvaProject.madn import Madn
from mpi4py import MPI

class Play():
    #dice action
    def move(diced):
        # count Puppets in start
        Madn.startCount = 0

        # count puppets in house
        for startSpots in Madn.groundCoordHouseSports[Madn.comm.Get_rank()]:
            if Madn.groundCoord[startSpots[0]][startSpots[1]] != "-":
                Madn.startCount += 1

        Madn.eprint("diced ", diced)
        Madn.eprint("Madn.startCount ", Madn.startCount)
        Madn.eprint("Madn.diceCount " , Madn.diceCount)

        # if all Puppets are in Home and you are in the first 3
        # @todo: change Madn.startCount == 4 to Madn.startCount - homeCount == 4
        if Madn.startCount == 4 and Madn.diceCount <= 1:
            Madn.diceCount += 1
            Madn.eprint("start.py startDice", "")
            if diced == 6:
                Play.moveToStartPoint()
                Madn.eprint("start.py diced==6", "")
        elif Madn.startCount == 4 and Madn.diceCount >= 2:
            # if its last dice
            Madn.diceCount += 1
            Madn.eprint("start.py else roundup", "")
            if diced == 6:
                Play.moveToStartPoint()
                Madn.eprint("start.py diced==6", "")
            else:
                Madn.eprint("in else", "")
                Madn.round += 1
                Madn.eprint("Madn.round ", Madn.round)

                #Madn.comm.Get_size() = 2
                #Madn.isOnTurn = 0
                # change whos turn it is
                if (Madn.comm.Get_size() - 1) > Madn.isOnTurn:
                    Madn.isOnTurn = Madn.isOnTurn + 1
                else:
                    Madn.isOnTurn = 0
                Madn.comm.bcast(Madn.isOnTurn, root=Madn.comm.Get_rank())

            Madn.diceCount = 0
        else:
            Madn.eprint("normal ", "move")
            # place for tactics
            # 

            #normal move
            if diced == 6:
                Madn.eprint("test", "test")
        Madn.diced = diced

    def moveToStartPoint():
        # add puppet to startPoint
        startSpotXforPlayer = Madn.groundCoordStartSports[Madn.comm.Get_rank()][1]
        startSpotYforPlayer = Madn.groundCoordStartSports[Madn.comm.Get_rank()][0]
        
        Madn.groundCoord[startSpotXforPlayer][startSpotYforPlayer] = Madn.comm.Get_rank()

        # remove puppet from House
        # get last Puppet Position in House
        myHouseArray = Madn.groundCoordHouseSports[Madn.comm.Get_rank()]
        lastHousePuppet = -1
        # iterate though Housepuppets
        for housePuppet in myHouseArray:
            # if there is a puppet in position check next
            Madn.eprint("map ", Madn.groundCoord[housePuppet[0]][housePuppet[1]])
            if Madn.groundCoord[housePuppet[0]][housePuppet[1]] != "-":
                lastHousePuppet += 1
                Madn.eprint("lastHousePuppet ", lastHousePuppet)

        # set empty
        houseSpotYforPlayer = myHouseArray[lastHousePuppet][0]
        houseSpotXforPlayer = myHouseArray[lastHousePuppet][1]
        Madn.eprint("houseSpotYforPlayer ", houseSpotYforPlayer)
        Madn.eprint("houseSpotXforPlayer ", houseSpotXforPlayer)
        Madn.eprint("test ", Madn.groundCoordHouseSports[Madn.comm.Get_rank()][3])
        Madn.groundCoord[houseSpotXforPlayer][houseSpotYforPlayer] = "-"

        # set playerStates
        # set Start Spot Count
        puppetPos = Madn.playerStates.index(houseSpotXforPlayer, houseSpotYforPlayer)
        Madn.eprint("puppetPos ", puppetPos)
        Madn.playerStates[Madn.comm.Get_rank()][1] = Madn.playerStates[Madn.comm.Get_rank()][1]-1
        Madn.playerStates[Madn.comm.Get_rank()][puppetPos] = [startSpotXforPlayer][startSpotYforPlayer]
