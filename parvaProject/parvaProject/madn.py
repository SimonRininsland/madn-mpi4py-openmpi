import sys
from pprint import pprint
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from mpi4py import MPI
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
        try:
            parent = MPI.Comm.Get_parent()
        except Exception as e:
            return (e)

        madn.comm = parent.Merge()

        msg = "Client is " + str(madn.comm.Get_rank() + 1) + " von " + str(madn.comm.Get_size()) + " in " + str(
            MPI.Get_processor_name())
        if madn.round == 0:
            self.setStart()
        return (msg)

    def createGame(self):
        mpi_info = MPI.Info.Create()
        mpi_info.Set("add-hostfile", "/home/mpirun/parvaProject/worker_hosts")

        try:
            madn.comm = MPI.COMM_SELF.Spawn(
                '/usr/bin/python3',
                args=['/home/mpirun/parvaProject/manage.py',
                      'runserver',
                      '0.0.0.0:8000'],
                maxprocs=1,
                info=mpi_info
            ).Merge()
        except Exception as e:
            return(e)

        msg = "Server is " + str(madn.comm.Get_rank() + 1) + " von " + str(madn.comm.Get_size()) + " in " + str(
            MPI.Get_processor_name())
        if madn.round == 0:
            self.setStart()
        return (msg)

    def dice(self, diced):
        # if it's my turn
        if madn.comm.Get_rank() == madn.isOnTurn:
            madn.isOnTurn = madn.comm.Get_rank()
            madn.diced = diced
            madn.comm.bcast(diced, root=madn.comm.Get_rank())
        else:
            madn.diced = madn.comm.bcast(madn.diced, root=madn.isOnTurn)
        madn.round += 1

    def setStart(self):
        madn.groundCoordMap[0][0] = 0
        madn.groundCoordMap[0][1] = 0
        madn.groundCoordMap[1][0] = 0
        madn.groundCoordMap[1][1] = 0
        madn.groundCoordMap[9][0] = 1
        madn.groundCoordMap[10][0] = 1
        madn.groundCoordMap[9][1] = 1
        madn.groundCoordMap[10][1] = 1

    def getStatus(self):
        # bcast dice and groundCoordMap
        madn.diced = madn.comm.bcast(madn.diced, root=madn.isOnTurn)
        madn.groundCoordMap = madn.comm.bcast(madn.groundCoordMap, root=madn.isOnTurn)

        return json.dumps([
                madn.isOnTurn,
                madn.diced,
                madn.comm.Get_rank(),
                madn.comm.Get_size()]
            + madn.groundCoordMap
            )


class madn():
    isOnTurn = 0
    diced = 0
    round = 0
    comm = MPI.COMM_WORLD

    # First is Start Point from Yellow

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

    # 0 - Yellow
    # 1 - Green
    # 2 - Red
    # 3 - Blue
    # 1. = AI(0).Real(1)
    # 2. = Start Spot Count
    # 3. = Park Spot Count
    # Default is AI and all in Park Position
    playerStates = [[0, 4, 0], [0, 4, 0], [0, 4, 0], [0, 4, 0]]
