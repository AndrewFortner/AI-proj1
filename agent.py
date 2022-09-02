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
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        r = observations[0]
        c = observations[1]
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
    
    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        dirs = [(2, (1, 0)), (3, (-1, 0)), (4, (0, 1)), (5, (0, -1))]
        r = observations[0]
        c = observations[1]
        get_environment().mark_maze_green(r, c)
        for d in dirs:
            r_mod = r
            c_mod = c
            r_mod += d[1][0]
            c_mod += d[1][1]
            if observations[d[0]] == 0 and (r_mod,c_mod) not in self.visited:
                self.visited.add((r_mod,c_mod))
                g = self.get_distance(r_mod, c_mod)
                h = self.heuristic(r_mod, c_mod)
                if g+h <= self.f:
                    get_environment().mark_maze_green(r_mod, c_mod)
                    heappush(self.queue, Cell(g + h, r_mod, c_mod))
                    self.backpointers[(r_mod, c_mod)] = (r, c)
                else:
                    self.lowest_above = min(self.lowest_above, g+h)
                    print("g+h: ", g+h)
        
        cell = self.queue[0]
        h, r2, c2 = cell.h, cell.r, cell.c
        if not self.travel_mode:
            cell = heappop(self.queue)
        dr = r2 - r
        dc = c2 - c
        action = get_action_index((dr, dc))
        if action is None:
            self.travel_mode = True
            print(r2, c2)
            next_move = self.get_next_step(r, c, r2, c2)
            print(next_move)
            dr = next_move[0] - r
            dc = next_move[1] - c
            action = get_action_index((dr, dc))
        else:
            self.travel_mode = False
        
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

