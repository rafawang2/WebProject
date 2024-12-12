import os, json
class Gomoku_game():
    def __init__(self,board_size=15) -> None:
        self.board_size = board_size
        self.current_player = -1
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.winner = 2
        self.move_log = []  # List to store move history
        self.step_cnt = 1
        
    def print_board(self):
        print("="*(self.board_size*2-1))
        for row in self.board:
            print(" ".join(map(str, row)))
        print("="*(self.board_size*2-1))
    
    def is_valid(self,r,c):
        if(self.board[r][c] == 0):
            return True
        else:
            return False
    
    def get_ValidMoves(self):
        positions = []
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] == 0:
                    positions.append((y, x))
        return positions
    
    def check_win(self, r, c, player):
        # 檢查橫向
        for col in range(max(0, c-4), min(self.board_size-4, c+1)):
            if all(self.board[r][col+i] == player for i in range(5)):
                return True
                
        # 檢查縱向
        for row in range(max(0, r-4), min(self.board_size-4, r+1)):
            if all(self.board[row+i][c] == player for i in range(5)):
                return True
                
        # 檢查右斜向下
        for i in range(-4, 1):
            if (0 <= r+i < self.board_size-4 and 
                0 <= c+i < self.board_size-4):
                if all(self.board[r+i+j][c+i+j] == player for j in range(5)):
                    return True
                    
        # 檢查左斜向下
        for i in range(-4, 1):
            if (0 <= r+i < self.board_size-4 and 
                0 <= c-i < self.board_size and 
                c-i >= 4):
                if all(self.board[r+i+j][c-i-j] == player for j in range(5)):
                    return True
        
        return False

    def is_win(self):
        # 檢查最後下棋的位置是否獲勝
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    if self.check_win(r, c, self.board[r][c]):
                        self.winner = self.board[r][c]
                        return self.winner
        
        # 如果沒有勝利者，檢查棋盤是否滿了
        if all(cell != 0 for row in self.board for cell in row):
            self.winner = 0
            return 0  # 平手
        
        return 2 # 遊戲繼續
    
    
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
    
    # def save_log_to_json(self, filename="static/Log/test_log.json"):
    #     """Saves the move log to a JSON file."""
    #     with open(filename, "w") as file:
    #         json.dump({"steps": self.move_log}, file, indent=4)
    def save_log_to_json(self, filename="Log/test_log.json"):
        """Saves the move log to a JSON file."""
        # 確保基於當前檔案的路徑
        base_dir = os.path.dirname(os.path.abspath(__file__))  # 當前檔案所在目錄
        full_path = os.path.join(base_dir, "static", filename)  # 靜態資料夾完整路徑
        directory = os.path.dirname(full_path)

        try:
            # 檢查目錄是否存在
            if not os.path.exists(directory):
                os.makedirs(directory)  # 創建目錄
                print(f"Directory created: {directory}")

            # 存檔
            with open(full_path, "w") as file:
                json.dump({"steps": self.move_log}, file, indent=4)
            self.move_log.clear()

            # 確認檔案是否正確存儲
            if os.path.exists(full_path):
                print(f"File saved successfully: {full_path}")
            else:
                print(f"Error: File not found after saving: {full_path}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def reset(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = -1
        self.winner = 2
    
    def make_move(self, r, c, player):
        self.board[r][c] = player
        self.current_player *= -1 # 換玩家
        

        
# game = Gomoku_game(15)
# game.play()