from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

class IdaStarSearchAgent(SearchAgent):
    """
    IDA* algorithm
    """
    def __init__(self):
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.f = -1
        self.lowest_above = 999999999
        self.queue = []
        self.visited = set()
        self.heuristic = manhattan_heuristic

    def reset(self):
        """
        Reset the agent
        """
        pass

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.f = -1
        self.action_info = init_info.actions
        self.lowest_above = 999999999
        self.queue = []
        self.visited = set()
        self.backpointers = {}
        self.travel_mode = False
        self.depth = 1
        self.num_beyond = 0
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        self.starting_r = observations[0]
        self.starting_c = observations[1]
        r = self.starting_r
        c = self.starting_c
        self.f = self.heuristic(r, c)
        get_environment().mark_maze_green(r, c)
        return self.action_info.random()

    def get_next_step(self, r1, c1, r2, c2):
        """
        return the next step when trying to get from current r1,c1 to target r2,c2
        """
        back_stack = []# cells between origin and r2,c2
        r, c = r2, c2 # back track from target
        while (r, c) in self.backpointers:
            print((r,c))
            r, c = self.backpointers[(r, c)]
            if (r1, c1) == (r, c): # if we find starting point, we need to move forward
                return back_stack # return the last step
            back_stack.append((r,c))
        return self.backpointers[(r1, c1)]
    
    def add_adj(self, observations):
        r = observations[0]
        c = observations[1]
        dirs = [(2, (1, 0)), (3, (-1, 0)), (4, (0, 1)), (5, (0, -1))]
        for d in dirs:
            r_mod = r + d[1][0]
            c_mod = c + d[1][1]
            if observations[d[0]] == 0 and (r_mod,c_mod) not in self.visited:
                self.visited.add((r_mod,c_mod))
                #Is our get_distance working?
                g = self.get_distance(r_mod, c_mod)
                h = self.heuristic(r_mod, c_mod)
                if g+h <= self.f and g <= self.depth:
                    get_environment().mark_maze_green(r_mod, c_mod)
                    #Is this adding correcrtly?
                    heappush(self.queue, Cell(g + h, r_mod, c_mod))
                    self.backpointers[(r_mod, c_mod)] = (r, c)
                elif g+h > self.f and g <= self.depth:
                    self.lowest_above = min(self.lowest_above, g+h)
                    print("g+h: ", g+h)
                elif g > self.depth:
                    self.num_beyond += 1

    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        
        self.add_adj(observations)
        #When there are no more valid nodes at this depth, set f to the 
        if not self.queue:
            if self.num_beyond == 0:
                self.f = self.lowest_above
            else:
                self.depth += 1
            self.visited.clear()
            self.num_beyond = 0
            self.lowest_above = 999999999
            get_environment().teleport(self, self.starting_r, self.starting_c)
            return None
        cell = heappop(self.queue)
        r = observations[0]
        c = observations[1]
        r2, c2 = cell.r, cell.c
        dr = r2 - r
        dc = c2 - c
        action = get_action_index((dr, dc))
        if action is None:
            print(r2, c2)
            #Are we allowed to teleport?
            get_environment().teleport(self, r2, c2)
        
        return action

    def end(self, time, reward):
        """
        at the end of an episode, the environment tells us the final reward
        """
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True

    def destroy(self):
        """
        After one or more episodes, this agent can be disposed of
        """
        return True
