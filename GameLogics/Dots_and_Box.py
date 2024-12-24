import os, json
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
        self.winner = 2
        self.move_log = []  # List to store move history
        self.step_cnt = 1
        
    def log_move(self, board, player, row, col):
        """Logs a move with its step, coordinates, and player."""
        self.move_log.append({
            "step": self.step_cnt,
            "board": [r[:] for r in board],  # Store a copy of the board
            "player": player,
            "row": row,
            "col": col
        })
        self.step_cnt += 1
    
    def save_log_to_json(self, filename="static/Log/test_Gomoku_log.json"):
        """Saves the move log to a JSON file."""
        # 確保基於當前檔案的路徑
        # base_dir = os.path.dirname(os.path.abspath(__file__))  # 當前檔案所在目錄
        # full_path = os.path.join(base_dir, "", filename)  # 靜態資料夾完整路徑
        directory = os.path.dirname("static/Log/DaB_log")

        try:
            # 檢查目錄是否存在
            if not os.path.exists(directory):
                os.makedirs(directory)  # 創建目錄
                print(f"Directory created: {directory}")

            # 存檔
            with open(filename, "w") as file:
                json.dump({"steps": self.move_log}, file, indent=4)
            self.move_log.clear()

            # 確認檔案是否正確存儲
            if os.path.exists(filename):
                print(f"File saved successfully: {filename}")
            else:
                print(f"Error: File not found after saving: {filename}")
        except Exception as e:
            print(f"Unexpected error: {e}")
     
    def getValidMoves(self,player=None):
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
  
    def make_move(self,row,col,player=None):
        if not self.is_valid(r = row,c = col):
            return
        self.board[row][col] = player
        self.log_move(self.board, player, row, col)
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