class DotsAndBox():
    def initialize_board(self,m, n):
        # 初始化一個(2*m-1) * (2*n-1)的二維陣列
        board = [[0 for _ in range(2*n-1)] for _ in range(2*m-1)]
        # 填入頂點(5)和合法邊(0)，以及未被佔領的格子(8)
        for i in range(2*m-1):
            for j in range(2*n-1):
                if i % 2 == 0 and j % 2 == 0:
                    # 填入頂點 5
                    board[i][j] = 5
                elif i % 2 == 1 and j % 2 == 1:
                    # 填入格子 8
                    board[i][j] = 8
                else:
                    # 填入合法邊 0
                    board[i][j] = 0
        return board
    
    def __init__(self,m,n):
        self.input_m = m
        self.input_n = n
        self.board_rows_nums = 2*m-1
        self.board_cols_nums = 2*n-1
        self.board = self.initialize_board(m=m,n=n)
        self.current_player = -1
        self.p1_scores = 0
        self.p2_scores = 0
    def getValidMoves(self):
        ValidMoves = []
        for i in range(self.board_rows_nums):
            for j in range(self.board_cols_nums):
                if self.board[i][j] == 0:
                    ValidMoves.append((i,j))
        return ValidMoves

    def is_valid(self,r,c):
        if r >= self.board_rows_nums or c >= self.board_cols_nums:
            return False
        if self.board[r][c] != 0:
            return False
        return True
    
    def checkBox(self,board):
        box_filled = False
        for i in range(self.input_m - 1):
            for j in range(self.input_n - 1):
                box_i = 2*i + 1
                box_j = 2*j + 1
                # 檢查該方格的四條邊是否都不為 0
                if (board[box_i][box_j] == 8 and
                    board[box_i-1][box_j] != 0 and
                    board[box_i+1][box_j] != 0 and
                    board[box_i][box_j-1] != 0 and
                    board[box_i][box_j+1] != 0):
                    
                    # 更新該方格的狀態
                    board[box_i][box_j] += self.current_player
                    if board[box_i][box_j] == 7:
                        self.p1_scores += 1
                    elif board[box_i][box_j] == 9:
                        self.p2_scores += 1
                    box_filled = True
        return box_filled
  
    def make_move(self,row,col,player):
        if not self.is_valid(r = row,c = col):
            return
        
        self.board[row][col] = player
        
        if not self.checkBox(board=self.board):    #沒有完成方形就換人
            self.current_player *= -1   #沒有完成方格，換下一人

    def isGameOver(self):
        for i in range(self.input_m - 1):
            for j in range(self.input_n - 1):
                if self.board[2*i+1][2*j+1] == 8:
                    return False
        return True

    def is_win(self):
        if self.isGameOver():
            if self.p1_scores > self.p2_scores:
                return -1
            elif self.p1_scores < self.p2_scores:
                return 1
            elif self.p1_scores == self.p2_scores:
                return 0
            else:
                return 2
        else:
            return 2
    
    def NewGame(self):
        self.current_player = -1
        self.board = self.initialize_board(self.input_m,self.input_n)
        self.p1_scores = 0
        self.p2_scores = 0