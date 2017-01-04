__author__ = 'user'

from CricketCLI import *
from pycricket import *
from kwutils import *
import logging

def main():


    logging.basicConfig(level = logging.INFO)

    'Start the game from the beginning.'

    teams = ["England", "Australia", "India", "Pakistan", "New Zealand", "South Africa", "Hong Kong"]
    team1_name = pick("Team 1", teams)
    teams.remove(team1_name)
    team2_name = pick("Team 2", teams)

    rules = CricketRules("Test Match")
    match = CricketMatch("Ashes", rules)

    team1 = CricketTeam(team1_name)
    team1.add_player(CricketPlayer("Keith"))
    team1.add_player(CricketPlayer("Jack"))
    team1.add_player(CricketPlayer("Oliver"))
    team1.add_player(CricketPlayer("Bruce"))


    team2 = CricketTeam(team2_name)
    team2.add_player(CricketPlayer("Jane"))
    team2.add_player(CricketPlayer("Rosie"))
    team2.add_player(CricketPlayer("Lynne"))
    team2.add_player(CricketPlayer("Li"))

    match.add_team(team1)
    match.add_team(team2)

    cli = CricketCLI(match)

    cli.cmdloop()

    try:
        pass

    except Exception as err:
        print(str(err))


    return


if __name__ == '__main__':
    main()
