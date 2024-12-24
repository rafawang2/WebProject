import json, os

BLACK = -1
WHITE = 1

class OthelloGame():
    def __init__(self, board_size):
        self.board_size=board_size
        self.current_player=BLACK   #黑棋先手
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        #設置棋盤中心初始狀態
        self.board[board_size//2][board_size//2]=WHITE
        self.board[board_size//2-1][board_size//2-1]=WHITE
        self.board[board_size//2-1][board_size//2]=BLACK
        self.board[board_size//2][board_size//2-1]=BLACK
        
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
        directory = os.path.dirname("static/Log/Othello_log")

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
    
    def getValidMoves(self, color):  #獲取指定顏色的所有有效走法
        moves = set()  #有效的走法位置
        for y, row in enumerate(self.board):    #y: 0~self.board_size-1, row:  self.board[y]
            for x, cell in enumerate(row):      #x: 0~self.board_size-1, cell: self.board[y][x]
                if cell == color:  #如果當前格子是玩家的棋子
                    #遍歷8個方向
                    for direction in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
                        flips = []  #要翻轉的棋子
                        
                        for size in range(1, self.board_size):  #探索從當前格子出發的每一個方向
                            ydir = y + direction[1] * size  #計算新的縱向座標
                            xdir = x + direction[0] * size  #計算新的橫向座標
                            
                            #檢查新的座標是否在棋盤範圍內
                            if xdir >= 0 and xdir < self.board_size and ydir >= 0 and ydir < self.board_size:
                                if self.board[ydir][xdir] == -color:  #如果是對方的棋子
                                    flips.append((ydir, xdir))  #需要翻轉
                                elif self.board[ydir][xdir] == 0:
                                    if len(flips) != 0:  #如果有棋子需要翻轉
                                        moves.add((ydir, xdir))  #則當前位置是有效的走法
                                    break  #不能再繼續擴展，跳出循環
                                else:  #如果是自己顏色的棋子，不能再繼續，跳出循環
                                    break
                            else:  #如果超出了棋盤範圍，跳出循環
                                break
        return list(moves)  #返回有效走法的位置列表
    
    def is_valid(self, r, c):
        position = (r,c)
        valids = self.getValidMoves(self.current_player)
        if position in valids:
            return True
        else:
            return False

    def executeMove(self, position):
        y, x = position
        self.board[y][x] = self.current_player  #直接落子

        #遍歷所有方向
        for direction in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
            flips = []
            valid_route = False  #用來標記是否找到有效的翻轉路徑

            # 從當前位置開始，沿著方向逐步搜尋，最大範圍為棋盤大小
            for size in range(1, self.board_size):
                ydir = y + direction[1] * size  # 計算新的縱向座標
                xdir = x + direction[0] * size  # 計算新的橫向座標

                #檢查是否超出棋盤範圍
                if xdir >= 0 and xdir < self.board_size and ydir >= 0 and ydir < self.board_size:
                    if self.board[ydir][xdir] == -self.current_player:  # 如果發現對方的棋子
                        flips.append((ydir, xdir))  # 將其加入翻轉列表
                    elif self.board[ydir][xdir] == self.current_player:  # 如果發現自己的棋子
                        if len(flips) > 0:  # 如果有對方棋子被翻轉，則標記為有效路徑
                            valid_route = True
                        break  # 條路徑結束，無需再繼續
                    else:  #如果發現空格，這條路徑無效，結束該方向的搜尋
                        break
                else:  #如果超出棋盤邊界，這條路徑無效，結束搜尋
                    break
            
            #如果該方向上存在有效的翻轉路徑
            if valid_route:
                #翻轉
                for flip in flips:
                    yflip, xflip = flip
                    self.board[yflip][xflip] = self.current_player


    def make_move(self, r, c, player = None):
        if self.is_valid(r, c):
            self.executeMove((r, c))
            self.log_move(self.board, player, r, c)
            # 新增檢查下一位的合法步
            next_player_valids = self.getValidMoves(-self.current_player)
            if next_player_valids:
                self.current_player=-self.current_player    # 換下一位
        else:
            raise Exception('invalid move')
    
    def is_win(self):
        white_valid_moves=len(self.getValidMoves(WHITE))
        black_valid_moves=len(self.getValidMoves(BLACK))
        if white_valid_moves==0 and black_valid_moves==0:
            black_count = 0
            white_count = 0
            for row in self.board:
                for cell in row:
                    if cell == WHITE:
                        white_count+=1
                    elif cell == BLACK:
                        black_count+=1
            if white_count>black_count:
                self.winner = WHITE
                return WHITE
            elif black_count>white_count:
                self.winner = BLACK
                return BLACK
            else:
                self.winner = 0
                return 0
        else:
            return 2
    
    def reset(self):
        self.current_player = -1
        
        #設置棋盤中心初始狀態
        self.board[self.board_size//2][self.board_size//2]=WHITE
        self.board[self.board_size//2-1][self.board_size//2-1]=WHITE
        self.board[self.board_size//2-1][self.board_size//2]=BLACK
        self.board[self.board_size//2][self.board_size//2-1]=BLACK
        
        self.step_cnt = 1
        self.winner = 2