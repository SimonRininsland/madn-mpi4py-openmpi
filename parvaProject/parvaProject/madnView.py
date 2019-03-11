from mpi4py import MPI
from pprint import pprint
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from parvaProject.start import Play
from parvaProject.madn import Madn
import json
import sys

class MadnView(View):
    def printplayground(self):
        return render(self, 'Madn-view.html')

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
            return (e)

        Madn.comm = parent.Merge()

        msg = "Client is " + str(Madn.comm.Get_rank() + 1) + " von " + str(Madn.comm.Get_size()) + " in " + str(
            MPI.Get_processor_name())

        return (msg)

    def createGame(self):
        mpi_info = MPI.Info.Create()
        mpi_info.Set("add-hostfile", "/home/mpirun/parvaProject/worker_hosts")

        try:
            comm = MPI.COMM_SELF.Spawn(
                'python3',
                args=['/home/mpirun/parvaProject/manage.py',
                      'runserver',
                      '0.0.0.0:8000'],
                maxprocs=1,
                info=mpi_info
            )
            Madn.comm = comm.Merge()
        except Exception as e:
            Madn.eprint("ERROR: ", str(e))
            return (e)

        msg = "Server is " + str(Madn.comm.Get_rank() + 1) + " von " + str(Madn.comm.Get_size()) + " in " + str(
            MPI.Get_processor_name())
        if Madn.round == 0:
            self.setStart()
        return (msg)

    def dice(self, diced):
        # if its your turn do:
        if Madn.comm.Get_rank() == Madn.isOnTurn:
            Play.move(diced)

    def setStart(self):
        Madn.eprint("CommSize: ", Madn.comm.Get_size())
        for player in range(Madn.comm.Get_size()):
            for spot in Madn.groundCoordHouseSports[player]:
                Madn.groundCoord[spot[0]][spot[1]] = player

    def getStatus(self):
         # bcast isOnTurn
        if Madn.comm.Get_rank() == Madn.isOnTurn:
            Madn.comm.bcast(Madn.isOnTurn, root=Madn.comm.Get_rank())
        else:
             Madn.isOnTurn = Madn.comm.bcast(Madn.isOnTurn, root=Madn.isOnTurn)

        # bcast dice
        if Madn.comm.Get_rank() == Madn.isOnTurn:
            Madn.comm.bcast(Madn.diced, root=Madn.comm.Get_rank())
        else:
            Madn.diced = Madn.comm.bcast(Madn.diced, root=Madn.isOnTurn)
        # bcast groundCoord
        if Madn.comm.Get_rank() == Madn.isOnTurn:
            Madn.comm.bcast(Madn.groundCoord, root=Madn.comm.Get_rank())
        else:
            Madn.groundCoord = Madn.comm.bcast(Madn.diced, root=Madn.isOnTurn)

        return json.dumps([
                  Madn.isOnTurn,
                  Madn.diced,
                  Madn.round,
                  Madn.comm.Get_rank(),
                  Madn.comm.Get_size()]
              + Madn.groundCoord
              )
