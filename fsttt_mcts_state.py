import numpy as np
from copy import deepcopy
from itertools import product
from mcts.base.base import BaseState, BaseAction


class FSTicTacToeState(BaseState):
    def __init__(self, current_player):
        self.board = np.zeros(shape=(4, 4), dtype=int)
        self.current_player = current_player
        # AI plays first, player plays second.
        if self.current_player == 1:
            self.mark = {1:'X', -1:'O', 0:'.'}
        # Player plays first, AI plays second.
        elif self.current_player == -1:
            self.mark = {1:'O', -1:'X', 0:'.'}

    def __repr__(self):
        board_str = ""
        for row in range(3, -1, -1):
            this_row = list(str(row)) + [self.mark[square] for square in self.board[row]]
            board_str += "{0} {1} {2} {3} {4}\n".format(*this_row)
        return "\n" + board_str + "  0 1 2 3\n"

    def get_current_player(self):
        return self.current_player

    def get_possible_actions(self):
        possible_actions = []
        for row, col in np.argwhere(self.board==0):
            possible_actions.append(Action(self.current_player, row, col))
        return possible_actions

    def take_action(self, action):
        new_state = deepcopy(self)
        new_state.board[action.row][action.col] = action.player
        new_state.current_player = self.current_player * -1
        return new_state

    def is_terminal(self):
        # Row win
        if 4 in abs(self.board.sum(axis=1)):
            return True
        # Column win
        if 4 in abs(self.board.sum(axis=0)):
            return True
        # Diagonal win \
        if abs(self.board.trace()) == 4:
            return True
        # Diagonal win /
        if abs(np.fliplr(self.board).trace()) == 4:
            return True
        # Four corners win
        if abs(self.board[[[0],[3]], [0,3]].sum()) == 4:
            return True
        # Four squares win
        for row, col in product(range(3), range(3)):
            if abs(self.board[[[row],[row+1]], [col,col+1]].sum()) == 4:
                return True
        # Is it a draw?
        if len(np.argwhere(self.board==0)) == 0:
            return True
        
        return False

    def get_reward(self):
        # Row win
        if 4 in self.board.sum(axis=1):
            return 1.0
        elif -4 in self.board.sum(axis=1):
            return -1.0
        # Column win
        if 4 in self.board.sum(axis=0):
            return 1.0
        elif -4 in self.board.sum(axis=0):
            return -1.0
        # Diagonal win \
        if abs(self.board.trace()) == 4:
            return self.board.trace() / 4
        # Diagonal win /
        if abs(np.fliplr(self.board).trace()) == 4:
            return np.fliplr(self.board).trace() / 4
        # Four corners win
        if abs(self.board[[[0],[3]], [0,3]].sum()) == 4:
            return self.board[[[0],[3]], [0,3]].sum() / 4
        # Four squares win
        for row, col in product(range(3), range(3)):
            if abs(self.board[[[row],[row+1]], [col,col+1]].sum()) == 4:
                return self.board[[[row],[row+1]], [col,col+1]].sum() / 4
        
        return False


class Action(BaseAction):
    def __init__(self, player, row, col):
        self.player = player
        self.row = row
        self.col = col

    def __str__(self):
        return str((self.row, self.col))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.row == other.row and self.col == other.col and self.player == other.player

    def __hash__(self):
        return hash((self.row, self.col, self.player))
