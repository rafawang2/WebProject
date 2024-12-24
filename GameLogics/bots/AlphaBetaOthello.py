from __future__ import absolute_import
from copy import deepcopy
import numpy as np
import math

def getValidMoves(board, color):
    moves = set()
    for y,x in zip(*np.where(board==color)):
        for direction in [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]:
            flips = []
            for size in range(1, len(board)):
                ydir = y + direction[1] * size
                xdir = x + direction[0] * size
                if xdir >= 0 and xdir < len(board) and ydir >= 0 and ydir < len(board):
                    if board[ydir][xdir]==-color:
                        flips.append((ydir, xdir))
                    elif board[ydir][xdir]==0:
                        if len(flips)!=0:
                            moves.add((ydir, xdir))
                        break
                    else:
                        break
                else:
                    break
    return np.array(list(moves))

def isValidMove(board, color, position):
    valids=getValidMoves(board, color)
    if len(valids)!=0 and (valids==np.array(position)).all(1).sum()!=0:
        return True
    else:
        return False

def executeMove(board, color, position):
    y, x = position
    board[y][x] = color
    for direction in [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]:
        flips = []
        valid_route=False
        for size in range(1, len(board)):
            ydir = y + direction[1] * size
            xdir = x + direction[0] * size
            if xdir >= 0 and xdir < len(board) and ydir >= 0 and ydir < len(board):
                if board[ydir][xdir]==-color:
                    flips.append((ydir, xdir))
                elif board[ydir][xdir]==color:
                    if len(flips)>0:
                        valid_route=True
                    break
                else:
                    break
            else:
                break
        if valid_route:
            board[tuple(zip(*flips))]=color

def alpha_beta_search(board, color, depth, alpha, beta, maximizing_player):
    """
    Alpha-beta pruning algorithm for Othello.

    Args:
        board: Current board state as a NumPy array.
        color: Current player's color (1 for BLACK, -1 for WHITE).
        depth: Remaining depth to search.
        alpha: Best score achievable by the maximizer so far.
        beta: Best score achievable by the minimizer so far.
        maximizing_player: True if current node is maximizer.

    Returns:
        A tuple containing the best score and the corresponding move.
    """
    valid_moves = getValidMoves(board, color)

    if depth == 0 or len(valid_moves) == 0:
        return evaluate_board(board, color), None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in valid_moves:
            simulated_board = board.copy()
            executeMove(simulated_board, color, tuple(move))
            eval, _ = alpha_beta_search(simulated_board, -color, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = tuple(move)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in valid_moves:
            simulated_board = board.copy()
            executeMove(simulated_board, color, tuple(move))
            eval, _ = alpha_beta_search(simulated_board, -color, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = tuple(move)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval, best_move

def evaluate_board(board, color):
    """
    Heuristic evaluation function for Othello.

    Args:
        board: Current board state as a NumPy array.
        color: Current player's color (1 for BLACK, -1 for WHITE).

    Returns:
        The evaluation score for the board from the perspective of the given player.
    """
    # Basic heuristic: difference in piece counts.
    player_count = np.sum(board == color)
    opponent_count = np.sum(board == -color)
    return player_count - opponent_count

class AlphaBeta():
    #set the infinity
    INFINITY = float('inf')
    WEIGHTS = [4, -3, 2, 2, 2, 2, -3, 4,
               -3, -4, -1, -1, -1, -1, -4, -3,
               2, -1, 1, 0, 0, 1, -1, 2,
               2, -1, 0, 1, 1, 0, -1, 2,
               2, -1, 0, 1, 1, 0, -1, 2,
               2, -1, 1, 0, 0, 1, -1, 2,
               -3, -4, -1, -1, -1, -1, -4, -3,
               4, -3, 2, 2, 2, 2, -3, 4]

    num_node = 0
    num_dup = 0
    node_list = []
    branch_list = [0,0,0]
    ply_maxmin = 4
    ply_alpha = 4
    """ Game engine that implements a simple fitness function maximizing the
    difference in number of pieces in the given color's favor. """
    def __init__(self):
        self.alpha_beta = True
    def getAction(self, board, color):
        """ Return a move for the given color that maximizes the difference in 
        number of pieces for that color. """
        board = np.array(board)
        if (self.alpha_beta == False):
            score, finalmove = self._minmax(board, color, AlphaBeta.ply_maxmin)
        else:
            score, finalmove = self._minmax_with_alpha_beta(board, color, AlphaBeta.ply_alpha)
        r, c = finalmove
        return (r,c)
        #maxmin function created by hyl
    def _minmax(self, board, color, ply):
        moves = self.getValidMoves(board, color)
        if not isinstance(moves, np.ndarray):
           score = self.heuristic(board, color)
           return score,None

        return_move = moves[0]
        bestscore = - AlphaBeta.INFINITY
        
        for move in moves:
            newboard = deepcopy(board)
            executeMove(newboard,color,move)

            score = self.min_score(newboard, -color, ply-1)
            if score > bestscore:
                bestscore = score
                return_move = move
        return (bestscore,return_move)

    #MAX_VALUE = AlphaBeta.INFINITY
    #MIN_VALUE = -MAX_VALUE


    def max_score(self, board, color, ply):
        moves = getValidMoves(board, color)
        
        if ply == 0:
           return self.heuristic(board, color)
        bestscore = -AlphaBeta.INFINITY
        for move in moves:     
            newboard = deepcopy(board)
            executeMove(newboard,color,move)
            score = self.min_score(newboard, -color, ply-1)
            if score > bestscore:
                bestscore = score
        return bestscore

    def min_score(self, board, color, ply):
        moves = getValidMoves(board,color)
        if ply == 0:
           return self.heuristic(board, color)
        bestscore = AlphaBeta.INFINITY
        for move in moves:
            if move in AlphaBeta.node_list:
                AlphaBeta.num_dup += 1
            if move not in AlphaBeta.node_list:
                AlphaBeta.node_list.append(move)
            newboard = deepcopy(board)
            executeMove(newboard,color,move)
            score = self.max_score(newboard, -color, ply-1)
            if score < bestscore:
                bestscore = score
        return bestscore

    def _minmax_with_alpha_beta(self, board, color, ply):
        moves = getValidMoves(board,color)
        if not isinstance(moves, np.ndarray):
            score = 0
            for row in board:
                for i in row:
                    if row[i] == color:
                        score += 1
            print(score)
            return score, None

        #print ply
        return_move = moves[0]
        bestscore = - AlphaBeta.INFINITY
        
        for move in moves:
            newboard = deepcopy(board)
            executeMove(newboard,color,move)
            AlphaBeta.branch_list[0] +=1
            score = self.min_score_alpha_beta(newboard, -color, ply-1, -AlphaBeta.INFINITY, AlphaBeta.INFINITY)
            if score > bestscore:
               bestscore = score
               return_move = move

        return (bestscore,return_move)

    def max_score_alpha_beta(self, board, color, ply, alpha, beta):
        if ply == 0:
            AlphaBeta.num_node +=1
            return self.heuristic(board, color)
        bestscore = -AlphaBeta.INFINITY
        for move in getValidMoves(board,color):
            
            newboard = deepcopy(board)
            executeMove(newboard,color,move)
            score = self.min_score_alpha_beta(newboard, -color, ply-1, alpha, beta)
            if score > bestscore:
                bestscore = score
            if bestscore >= beta:
                return bestscore
            alpha = max (alpha,bestscore)
        return bestscore

    def min_score_alpha_beta(self, board, color, ply, alpha, beta):
          if ply == 0:
             return self.heuristic(board, color)
          bestscore = AlphaBeta.INFINITY
          for move in getValidMoves(board, color):
              newboard = deepcopy(board)
              executeMove(newboard,color,move)
              score = self.max_score_alpha_beta(newboard, -color, ply-1, alpha, beta)
              if score < bestscore:
                 bestscore = score
              if bestscore <= alpha:
                 return bestscore
              beta = min(beta,bestscore)
          return bestscore

    def heuristic(self, board, color):
        return  5* self.cornerweight(color, board) + 3* self._get_cost(board, color)

    def cornerweight(self, color, board):
        total = 0
        for i in range(64):
            if board[i // 8][i % 8] == color:
                total += AlphaBeta.WEIGHTS[i]
            elif board[i // 8][i % 8] == -color:
                total -= AlphaBeta.WEIGHTS[i]
        return total

    def get_squares(self,board,color):
        squares=[]
        for y in range(8):
            for x in range(8):
                if board[x][y]==color:
                    squares.append((x,y))
        return squares

    def greedy(self, board, color, move):
        """ Return the difference in number of pieces after the given move 
        is executed. """

        # Create a deepcopy of the board to preserve the state of the actual board
        newboard = deepcopy(board)
        executeMove(newboard, color, move)
        
        # Count the # of pieces of each color on the board
        num_pieces_op = len(self.get_squares(newboard, color*-1))
        num_pieces_me = len(self.get_squares(newboard, color))

        # Return the difference in number of pieces
        return num_pieces_me - num_pieces_op

    def _get_cost(self, board, color):
        """ Return the difference in number of pieces after the given move 
        is executed. """

        # Count the # of pieces of each color on the board
        def count(board, color):
            score = 0
            for row in board:
                for i in row:
                    if row[i] == color:
                        score += 1
            return score
        num_pieces_op = count(board, -color)
        num_pieces_me = count(board, color)
        #print "_get_cost" + str(num_pieces_me - num_pieces_op)
        # Return the difference in number of pieces
        return num_pieces_me - num_pieces_op
