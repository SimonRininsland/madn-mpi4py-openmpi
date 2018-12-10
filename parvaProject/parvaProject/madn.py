from mpi4py import MPI
from pprint import pprint
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
import json


class MadnView(View):
    def printplayground(self):
        return render(self, 'madn-view.html')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.playerStates = [[0, 4, 0], [0, 4, 0], [0, 4, 0], [0, 4, 0]]
        args = dict(request.POST)

        if "createGame" in args:
            # Set options
            i = 0
            while i < 4:
                if "createGame[" + str(i) + "][value]" in args:
                    self.playerStates[int(args["createGame[" + str(i) + "][value]"][0])] = [1, 4, 0]
                i += 1
            return HttpResponse(self.createGame())
        elif "joinGame" in args:
            return HttpResponse(self.joinGame())
        elif "dice" in args:
            return HttpResponse(self.dice(int(args["dice"][0])))
        elif "getStatus" in args:
            return HttpResponse(self.getStatus())

    def joinGame(self):
        pprint(MPI.Comm)
        try:
            parent = MPI.Comm.Get_parent()
        except Exception as e:
            pprint("test")
            return (e)

        madn.comm = parent.Merge()

        msg = "Client is " + str(madn.comm.Get_rank() + 1) + " von " + str(madn.comm.Get_size()) + " in " + str(
            MPI.Get_processor_name())

        return (msg)

    def createGame(self):
        mpi_info = MPI.Info.Create()
        mpi_info.Set("add-hostfile", "/home/mpirun/parvaProject/worker_hosts")

        try:
            comm = MPI.COMM_SELF.Spawn(
                '/usr/bin/python3',
                args=['/home/mpirun/parvaProject/manage.py',
                      'runserver',
                      '0.0.0.0:8000'],
                maxprocs=1,
                info=mpi_info
            )
            madn.comm = comm.Merge()
        except Exception as e:
            pprint(e)
            return (e)

        msg = "Server is " + str(madn.comm.Get_rank() + 1) + " von " + str(madn.comm.Get_size()) + " in " + str(
            MPI.Get_processor_name())
        if madn.round == 0:
            self.setStart()
        return (msg)

    def dice(self, diced):
        # if it's round 0
        startCount = 0
        for startSpots in madn.groundCoordHouseSports[madn.comm.Get_rank()]:
            if madn.groundCoord[startSpots[0]][startSpots[1]] != "-":
                startCount+=1

        # if all Puppets are in Home
        if startCount == 4 & madn.diceCount <= 3:
            madn.diceCount += 1
            if diced == 6:
                madn.groundCoord[madn.groundCoordStartSports[madn.comm.Get_rank()][0]][
                    madn.groundCoordStartSports[madn.comm.Get_rank()][1]] = madn.comm.Get_rank()
                madn.round += 1
                madn.diceCount = 0
        else:
            madn.round += 1
        madn.diced = diced

    def doStep(self):
        pprint("asd")

    def setStart(self):
        pprint(madn.comm.Get_size())
        for player in range(madn.comm.Get_size()):
            for spot in madn.groundCoordHouseSports[player]:
                madn.groundCoord[spot[0]][spot[1]] = player

    def getStatus(self):
        # bcast dice
        if madn.comm.Get_rank() == madn.isOnTurn:
            madn.comm.bcast(madn.diced, root=madn.comm.Get_rank())
        else:
            madn.diced = madn.comm.bcast(madn.diced, root=madn.isOnTurn)
        # bcast groundCoord
        if madn.comm.Get_rank() == madn.isOnTurn:
            madn.comm.bcast(madn.groundCoord, root=madn.comm.Get_rank())
        else:
            madn.groundCoord = madn.comm.bcast(madn.diced, root=madn.isOnTurn)

        return json.dumps([
                              madn.isOnTurn,
                              madn.diced,
                              madn.round,
                              madn.comm.Get_rank(),
                              madn.comm.Get_size()]
                          + madn.groundCoord
                          )


class madn():
    isOnTurn = 0
    diced = 0
    round = 0
    diceCount = 0
    comm = MPI.COMM_WORLD

    # First is Start Point from Yellow

    groundCoord = [['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                   ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']]

    groundCoordMap = [['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                      ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']]

    # Start Spots: Player 0, Player 1, Player 2, Player 3
    groundCoordStartSports = [[0, 4], [6, 0], [10, 4], [6, 10]]

    # HouseSpots: Player 0, Player 1, Player 2, Player 3
    groundCoordHouseSports = [[[0, 0], [0, 1], [1, 0], [1, 1]],
                              [[0, 9], [0, 10], [1, 9], [1, 10]],
                              [9, 9], [10, 9], [10, 10], [9, 10],
                              [[9, 0], [10, 0], [9, 1], [10, 1]]]

    # 0 - Yellow
    # 1 - Green
    # 2 - Red
    # 3 - Blue
    # 1. = AI(0).Real(1)
    # 2. = Start Spot Count
    # 3. = Park Spot Count
    # 4. = First Puppet
    # 5. = Second Puppet
    # 6. = Third Puppet
    # 7. = Fourth Puppet
    # Default is AI and all in Park Position
    playerStates = [[0, 4, 0], [0, 4, 0], [0, 4, 0], [0, 4, 0]]
