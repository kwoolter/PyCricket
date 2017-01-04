__author__ = 'user'

import logging
from kwutils import *
from collections import deque
import random


class CricketPlayer():

    BOWLING = "BOWLING"
    BATTING = "BATTING"
    SPEED = "SPEED"
    CATCHING = "CATCHING"
    LUCK = "LUCK"
    SKILLS = (SPEED, BATTING, BOWLING, CATCHING, LUCK)

    def __init__(self, name: str):
        self.name = name

        # populate skills with random values
        self.skills = {}
        for skill in CricketPlayer.SKILLS:
            self.skills[skill] = random.random()

    def __str__(self):
        description = self.name
        return description

    def get_skill(self, skill : str):
        if skill not in self.skills.keys():
            return None
        else:
            return self.skills[skill]

    def increase_skill(self, skill : str, increment : float):
        if skill in self.skills.keys():
            self.skills[skill] += increment




class CricketDelivery():
    RUNS = 0
    NO_BALL = 1
    WIDE = 2
    BYES = 3
    WICKET = 4
    DOT = 5

    DESCRIPTION = ("Shot", "No Ball", "Wide", "Byes", "Wicket", "Dot")

    def __init__(self, type, runs=0, bowler: CricketPlayer = None, batsmen: CricketPlayer = None):
        self.runs = runs
        self.type = type
        self.bowler = bowler
        self.batsmen = batsmen

    def __str__(self):
        description = "%s to %s:%s" % (self.bowler, self.batsmen, CricketDelivery.DESCRIPTION[self.type])
        if self.runs != 0:
            description += ": runs %i" % self.runs
        return description


class CricketRules():
    RUNS = -999

    runs_map = {CricketDelivery.WICKET: -5,
                CricketDelivery.NO_BALL: 2,
                CricketDelivery.WIDE: 2,
                CricketDelivery.RUNS: -999,
                CricketDelivery.BYES: -999,
                CricketDelivery.DOT: 0

                }

    def __init__(self, name: str):
        self.name = name
        self.max_teams = 2
        self.max_player = 8
        self.innings = 1
        self.overs_per_innings = 3
        self.deliveries_per_over = 6

    @staticmethod
    def runs(delivery_type_id):
        return CricketRules.runs_map[delivery_type_id]


class CricketTeam():
    def __init__(self, name: str):
        self.name = name
        self.list_players = []

    def add_player(self, new_player: CricketPlayer):
        logging.info("Trying to add player %s to team %s." % (new_player.name, self.name))
        self.list_players.append(new_player)

    def __str__(self):
        return self.name

    @property
    def players(self):
        return len(self.list_players)

    def print(self):
        print("Team %s" % self.name)
        for i in range(len(self.list_players)):
            print("%i. %s" % (i + 1, self.list_players[i]))


class CricketOver():
    READY = 0
    PLAYING = 1
    FINISHED = 2
    DESCRIPTION = ("Ready", "Playing", "Finished")

    def __init__(self, bowler: CricketPlayer = None, max_deliveries=6):
        self.deliveries = []
        self.max_deliveries = max_deliveries
        self.bowler = bowler

    def bowl(self, new_delivery: CricketDelivery):

        if len(self.deliveries) >= self.max_deliveries:
            raise (Exception("Already bowled maximum number of deliveries %i," % self.max_deliveries))

        # Always set the bowler of the delivery to who is currently bowling
        new_delivery.bowler = self.bowler

        self.deliveries.append(new_delivery)

    def batsmen_stats(self, batsmen: CricketPlayer):
        runs = 0
        balls = 0
        status = "NOT OUT"

        for delivery in self.deliveries:
            if delivery.batsmen == batsmen:
                runs += delivery.runs
                balls += 1
                if delivery.type == CricketDelivery.WICKET:
                    status = "OUT"

        return runs, balls, status

    def bowler_stats(self, bowler : CricketPlayer):
        if self.bowler == bowler:
            return self.runs, self.balls, self.wickets
        else:
            return 0,0,0

    @property
    def state(self):
        if len(self.deliveries) == 0:
            state = CricketOver.READY
        elif len(self.deliveries) < self.max_deliveries:
            state = CricketOver.PLAYING
        else:
            state = CricketOver.FINISHED

        return state

    @staticmethod
    def balls_to_overs(balls: int):

        return balls//6 + ((balls % 6) * 0.1)

    @property
    def balls(self):
        return len(self.deliveries)

    @property
    def runs(self):
        count = 0
        for delivery in self.deliveries:
            count += delivery.runs
        return count

    @property
    def wickets(self):
        count = 0
        for delivery in self.deliveries:
            if delivery.type == CricketDelivery.WICKET:
                count += 1
        return count

    def __str__(self):
        description = "Bowler: %s, State:%s\n" % (self.bowler, CricketOver.DESCRIPTION[self.state])
        for i in range(len(self.deliveries)):
            description += "%i. %s\n" % (i + 1, str(self.deliveries[i]))

        return description

    def print(self):
        print(str(self))

    def score(self):

        return self.runs, self.balls, self.wickets


class CricketInnings():
    READY = 0
    PLAYING = 1
    FINISHED = 2

    DESCRIPTION = ("Ready", "Playing", "Finished")

    def __init__(self, batting_team: CricketTeam, bowling_team: CricketTeam, max_overs=2):
        self.batting_team = batting_team
        self.bowling_team = bowling_team
        self.max_overs = max_overs
        self.overs = []

        self.bowlers = deque(self.bowling_team.list_players)
        self.batsmen = deque(self.batting_team.list_players)
        self.batsmen_in = deque()
        self.batsmen_out = deque()

    @property
    def current_batsmen(self):
        if len(self.batsmen_in) < 1:
            return None
        else:
            return self.batsmen_in[0]

    @property
    def current_bowler(self):
        if len(self.bowlers) < 1:
            return None
        else:
            return self.bowlers[0]

    def start(self):
        logging.info("Starting innings: batting %s, bowling %s" % (self.batting_team.name, self.bowling_team.name))

        # Get the first two batsmen
        self.batsmen_in.append(self.batsmen.popleft())
        self.batsmen_in.append(self.batsmen.popleft())

        # Start the first over
        first_over = CricketOver(bowler=self.current_bowler)

        self.overs.append(first_over)

    def bowl(self, delivery: CricketDelivery):

        # If the current over has finished then start a new one...
        if self.current_over.state == CricketOver.FINISHED:
            logging.info("Starting a new over")

            # put the current bowler to the back of the queue
            self.bowlers.rotate(-1)

            # Swap the facing batsmen over
            self.batsmen_in.reverse()

            # Start the new over
            self.overs.append(CricketOver(bowler=self.current_bowler))

        logging.info("New delivery %s for over %i: %s to %s" % (
        str(delivery), len(self.overs), self.current_bowler, self.current_batsmen))

        # set the facing batsmen for the delivery
        delivery.batsmen = self.current_batsmen

        self.current_over.bowl(delivery)


        # If the batsmen scored an odd number of runs then swap them over
        if delivery.type in (CricketDelivery.RUNS, CricketDelivery.BYES) and delivery.runs % 2 > 0:
            self.batsmen_in.reverse()

        # Else if there was a wicket bring in the new batsmen to face the next delivery
        elif delivery.type == CricketDelivery.WICKET:
            logging.info("Batsmen %s is out!" % self.current_batsmen)
            self.batsmen_out.append(self.batsmen_in.popleft())

            if len(self.batsmen) > 0:
                self.batsmen_in.appendleft(self.batsmen.popleft())
                logging.info("New Batsmen %s" % self.current_batsmen)

        if self.state == CricketInnings.FINISHED:
            runs, wickets, overs = self.score()
            raise (
            Exception("Innings over: %s score %i for %i after %.1f overs" % (self.batting_team, runs, wickets, overs)))

        if self.current_over.state == CricketOver.FINISHED:
            raise (Exception("Over %i completed." % len(self.overs)))

    def print(self):
        print("Batting %s, bowling %s : %s" % (self.batting_team.name,
                                               self.bowling_team.name,
                                               CricketInnings.DESCRIPTION[self.state]))

        for i in range(len(self.overs)):
            print("Over %i of %i." % (i + 1, len(self.overs)))
            self.overs[i].print()

        runs, wickets, overs = self.score()

        print("%s score %i for %i after %.1f overs" % (self.batting_team, runs, wickets, overs))

    def score_card(self):
        print("Batsmen\t\tRuns\tBalls\tStatus")
        for batsmen in self.batting_team.list_players:
            runs, balls, status = self.batsmen_stats(batsmen)
            print("%-10s\t%#4i\t%#4i\t%s" % (batsmen.name, runs, balls, status))

        print("\nBowler\t\tRuns\tOvers\tWickets")
        for bowler in self.bowlers:
            runs, balls, wickets = self.bowler_stats(bowler)
            print("%-10s\t%#4i\t%4.1f\t%#4i" % (bowler.name, runs, CricketOver.balls_to_overs(balls), wickets))


    def batsmen_stats(self, batsmen: CricketPlayer):
        runs = 0
        balls = 0
        over_status = ""

        for over in self.overs:
            over_runs, over_balls, over_status = over.batsmen_stats(batsmen)
            runs += over_runs
            balls += over_balls

        return runs, balls, over_status

    def bowler_stats(self, bowler: CricketPlayer):
        runs = 0
        balls = 0
        wickets = 0

        for over in self.overs:
            over_runs, over_balls, over_wickets = over.bowler_stats(bowler)
            runs += over_runs
            balls += over_balls
            wickets += over_wickets

        return runs, balls, wickets


    def score(self):
        runs = 0
        wickets = 0
        balls = 0

        for over in self.overs:
            new_runs, new_balls, new_wickets = over.score()
            runs += new_runs
            wickets += new_wickets
            balls += new_balls

        # logging.info("balls=%.1f" % overs)

        return runs, wickets, CricketOver.balls_to_overs(balls)

    @property
    def current_over(self):
        if len(self.overs) == 0:
            return None
        else:
            return self.overs[-1]

    @property
    def state(self):

        runs, wickets, overs = self.score()

        # Check if all out
        if wickets == self.batting_team.players - 1:
            state = CricketInnings.FINISHED
        # No overs or nothing started so ready to start
        elif len(self.overs) == 0 or self.overs[0].state == CricketOver.READY:
            state = CricketInnings.READY
        # Some overs so in progress
        elif len(self.overs) < self.max_overs:
            state = CricketInnings.PLAYING
        # Else final over, are we still playing?
        else:
            state = CricketInnings.FINISHED
            final_over = self.overs[-1]
            if final_over.state != CricketOver.FINISHED:
                state = CricketInnings.PLAYING

        return state


# CricketMatch Class
#
class CricketMatch():

    READY = 0
    PLAYING = 1
    FINISHED = 2
    DESCRIPTION = ("Ready", "Playing", "Finished")

    def __init__(self, name: str, rules: CricketRules):
        self.name = name
        self.list_teams = []
        self.rules = rules
        self.innings = []

    def add_team(self, new_team: CricketTeam):

        logging.info("Trying to add team %s to match %s." % (new_team.name, self.name))
        if len(self.list_teams) >= self.rules.max_teams:
            logging.warning("Already got enough teams for match %s" % self.name)
            raise (Exception("You can only have %i teams in a %s match." % (self.rules.max_teams, self.rules.name)))
        else:
            logging.info("Team %s added to match %s." % (new_team.name, self.name))
            self.list_teams.append(new_team)

    def print(self):
        print("Match %s (%s) - %s" % (self.name, self.rules.name, CricketMatch.DESCRIPTION[self.state]))
        for i in range(len(self.list_teams)):
            self.list_teams[i].print()

        for i in range(len(self.innings)):
            print("\nInnings %i" % (i + 1))
            self.innings[i].print()

        print("Match Summary")
        scores = self.score()
        for team in scores.keys():
            print("Team %s has scored a total of %i runs" % (team.name, scores[team]))

    def score_card(self):
        print("Match %s (%s) - %s" % (self.name, self.rules.name, CricketMatch.DESCRIPTION[self.state]))
        for i in range(len(self.innings)):
            print("\nInnings %i" % (i + 1))
            self.innings[i].score_card()

    def score(self):
        team_scores = {}
        for innings in self.innings:
            runs, wickets, overs = innings.score()
            if innings.batting_team not in team_scores.keys():
                team_scores[innings.batting_team] = 0
            team_scores[innings.batting_team] += runs

        return team_scores

    # Start the match
    def start(self):

        if len(self.list_teams) != 2:
            raise (Exception("You need 2 teams to start a game; you have %i" % len(self.list_teams)))

        teams = self.list_teams.copy()

        self.batting_team = pick("Batting side", teams)

        teams.remove(self.batting_team)

        self.bowling_team = pick("Bowling side", teams, auto_pick=True)

        self.innings = []
        innings = CricketInnings(self.batting_team, self.bowling_team, self.rules.overs_per_innings)

        self.innings.append(innings)
        innings.start()

    @property
    def state(self):

        state = CricketMatch.PLAYING

        if len(self.innings) == 0 or self.innings[0].state == CricketInnings.READY:
            state = CricketMatch.READY
        elif len(self.innings) == self.rules.innings * 2:
            if self.innings[-1].state == CricketInnings.FINISHED:
                state = CricketMatch.FINISHED

        return state

    @property
    def current_innings(self):
        if len(self.innings) == 0:
            return None
        else:
            return self.innings[-1]

    def bowl(self, delivery: CricketDelivery):

        # Check to see if the match has not finished
        if self.state != CricketMatch.FINISHED:

            # Check to see if the current innings is over...
            if self.current_innings.state == CricketInnings.FINISHED:
                logging.info("Starting a new innings")

                # Swap teams over
                temp = self.bowling_team
                self.bowling_team = self.batting_team
                self.batting_team = temp

                logging.info("%s batting, %s bowling." % (self.batting_team, self.bowling_team))

                new_innings = CricketInnings(self.batting_team, self.bowling_team, self.rules.overs_per_innings)
                new_innings.start()
                self.innings.append(new_innings)

            self.current_innings.bowl(delivery)

            # If the match has finished...
            if self.state == CricketMatch.FINISHED:
                print("\nIt's all over!")
                self.print()
                raise (Exception("Match between %s and %s has finished." % (self.batting_team, self.bowling_team)))

            # The innings is over but the match is still going...
            elif self.current_innings.state == CricketInnings.FINISHED:

                # Swap teams over
                temp = self.bowling_team
                self.bowling_team = self.batting_team
                self.batting_team = temp

                runs, wickets, overs = self.current_innings.score()

                raise (Exception(
                    "Innings of %s completed: %i for %i off %.1f overs" % (self.batting_team, runs, wickets, overs)))

        else:
            self.print()
            raise (Exception("Match between %s and %s has finished." % (self.batting_team, self.bowling_team)))

class CricketBrain():

    # How much does luck come into determining delivery outcome
    LUCK_MULTIPLIER = 10

    # How much does skill come into determining delivery outcome
    SKILL_MULTIPLIER = 10

     # How much does speed come into determining delivery outcome
    SPEED_MULTIPLIER = 5

    # Determine bowling outcome
    ACCURATE_BOWL_LIMIT = 7
    NO_BALL_LIMIT = 0
    WIDE_LIMIT = 5

    # Determine shot outcome
    SHOT_LIMIT = 8
    WICKET_LIMIT = 1

    # Skill award for successful play
    SKILL_BONUS = 0.1

    def __init__(self):
        pass

    @staticmethod
    def delivery(batsmen : CricketPlayer, bowler : CricketPlayer):
        """Use player stats to calculate what delivery a bowler will deliver to a batsmen."""
        type = CricketDelivery.DOT
        runs = 0


        # Get the bowler's skill stats
        bowling_skill = bowler.get_skill(CricketPlayer.BOWLING) * CricketBrain.SKILL_MULTIPLIER
        bowling_speed = bowler.get_skill(CricketPlayer.SPEED) * CricketBrain.SPEED_MULTIPLIER
        bowling_luck = bowler.get_skill(CricketPlayer.LUCK) * random.random() * CricketBrain.LUCK_MULTIPLIER

        # Get the batsmen's skill stats
        batting_skill = batsmen.get_skill(CricketPlayer.BATTING) * CricketBrain.SKILL_MULTIPLIER
        batting_speed = batsmen.get_skill(CricketPlayer.SPEED) * CricketBrain.SPEED_MULTIPLIER
        batting_luck = batsmen.get_skill(CricketPlayer.LUCK) * random.random() * CricketBrain.LUCK_MULTIPLIER

        # Calculate the batsmens's and bowler's chances
        batsmen_chance = (batting_skill + batting_luck - bowling_speed)
        bowling_chance = (bowling_skill + bowling_luck)

        print("Delivery calculator stats:")
        print("bowler skill=%.3f speed=%.3f luck=%.3f chance=%.3f, batsmen skill=%.3f speed=%.3f luck=%.3f chance=%.3f" %
              (bowling_skill, bowling_speed, bowling_luck, bowling_chance,
               batting_skill, batting_speed, batting_luck, batsmen_chance))

        # See if the bowler bowls an accurate ball...
        if bowling_chance > CricketBrain.ACCURATE_BOWL_LIMIT:

            logging.info("Accurate ball")

            # Give the bowler a skill bonus for bowling an accurate ball
            bowler.increase_skill(CricketPlayer.BOWLING, CricketBrain.SKILL_BONUS)

            # If the batsmen is good enough to make a shot...
            if batsmen_chance >= CricketBrain.SHOT_LIMIT:

                logging.info("Make a shot")

                # Make the delivery some runs...
                type = CricketDelivery.RUNS

                # ...and use the batsmen's skills to determine how many runs.
                runs = ((batting_skill + batting_luck + batting_speed) * 6/15) // 1

                # Give the batsmen a skill bonus for getting some runs
                batsmen.increase_skill(CricketPlayer.BATTING, CricketBrain.SKILL_BONUS)

            # Else see if the batsmen can't defend their wicket...
            elif batsmen_chance < CricketBrain.WICKET_LIMIT:

                logging.info("Wicket fallen")

                # Make the delivery a wicket
                type = CricketDelivery.WICKET

                # give the bowler a skill bonus for getting a wicket
                bowler.increase_skill(CricketPlayer.BOWLING, CricketBrain.SKILL_BONUS)

        # If the ball was not accurate then see what happens...
        else:
            if bowling_chance < CricketBrain.NO_BALL_LIMIT:

                logging.info("No ball")
                type = CricketDelivery.NO_BALL
                runs = CricketRules.runs(type)

            elif bowling_chance < CricketBrain.WIDE_LIMIT:

                logging.info("Wide")
                type = CricketDelivery.WIDE
                runs = CricketRules.runs(type)

        # Create the delivery that the brain has calculated
        new_delivery = CricketDelivery(type, runs, bowler, batsmen)

        return new_delivery