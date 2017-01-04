__author__ = 'user'

import cmd
from kwutils import *
from pycricket import *

class CricketCLI(cmd.Cmd):

    intro = "Welcome to the PyCricket CLI.\nType 'start' got get going!"
    prompt = "What next?"


    def __init__(self, match : CricketMatch):

        super(CricketCLI, self).__init__()
        self.match = match

    def do_quit(self, arg):
        if confirm("Are you sure you want to quit?"):
            exit(0)

    def do_start(self, arg):
        self.match.start()

    def do_auto(self, arg):

        try:
            current_innings = self.match.current_innings
            batsmen = current_innings.current_batsmen
            bowler = current_innings.current_bowler

            if is_numeric(arg):
                loops = int(arg)
            else:
                loops = 1

            for i in range(loops):
                #batsmen = CricketPlayer("Ace")
                #bowler = CricketPlayer("Bad Boy")
                new_delivery = CricketBrain.delivery(batsmen, bowler)
                self.match.bowl(new_delivery)
                #print(new_delivery)

        except Exception as err:
            print(str(err))

    def do_test(self, arg):
        try:

            if is_numeric(arg):
                loops = int(arg)
            else:
                loops = 1

            for i in range(loops):
                batsmen = CricketPlayer("Ace")
                bowler = CricketPlayer("Bad Boy")
                new_delivery = CricketBrain.delivery(batsmen, bowler)
                print(new_delivery)

        except Exception as err:
            print(str(err))


    def do_bowl(self, arg):

        try:
            if is_numeric(arg):
                type_id = int(arg) - 1
                if type_id not in range(len(CricketDelivery.DESCRIPTION)):
                    raise(Exception("Invalid delivery type %i" % type_id))
            else:
                type = pick("delivery",CricketDelivery.DESCRIPTION)
                type_id = CricketDelivery.DESCRIPTION.index(type)

            runs = CricketRules.runs(type_id)
            if runs == CricketRules.RUNS:
                runs = pick("Runs", (1,2,3,4,5,6,0))
            self.match.bowl(CricketDelivery(type_id, runs))

        except Exception as err:
            print(str(err))

    def do_score(self, arg):
        self.match.score_card()


    def do_print(self, arg):
        self.match.print()

