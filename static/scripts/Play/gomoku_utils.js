class GomokuGame {
    constructor(boardSize = 10) {
        this.boardSize = boardSize;
        // this.current_player = -1; // -1 for black, 1 for white
        this.board = Array.from({ length: boardSize }, () => Array(boardSize).fill(0));
        this.winner = 0;
    }

    isValid(r, c) {
        return this.board[r][c] === 0;
    }

    getValidMoves() {
        const positions = [];
        for (let y = 0; y < this.boardSize; y++) {
            for (let x = 0; x < this.boardSize; x++) {
                if (this.board[y][x] === 0) {
                    positions.push([y, x]);
                }
            }
        }
        return positions;
    }

    checkWin(r, c, player) {
        // Check horizontal
        for (let col = Math.max(0, c - 4); col <= Math.min(this.boardSize - 5, c); col++) {
            if (Array.from({ length: 5 }).every((_, i) => this.board[r][col + i] === player)) {
                return true;
            }
        }

        // Check vertical
        for (let row = Math.max(0, r - 4); row <= Math.min(this.boardSize - 5, r); row++) {
            if (Array.from({ length: 5 }).every((_, i) => this.board[row + i][c] === player)) {
                return true;
            }
        }

        // Check diagonal (top-left to bottom-right)
        for (let i = -4; i <= 0; i++) {
            if (
                r + i >= 0 &&
                r + i + 4 < this.boardSize &&
                c + i >= 0 &&
                c + i + 4 < this.boardSize &&
                Array.from({ length: 5 }).every((_, j) => this.board[r + i + j][c + i + j] === player)
            ) {
                return true;
            }
        }

        // Check diagonal (top-right to bottom-left)
        for (let i = -4; i <= 0; i++) {
            if (
                r + i >= 0 &&
                r + i + 4 < this.boardSize &&
                c - i >= 0 &&
                c - i - 4 < this.boardSize &&
                Array.from({ length: 5 }).every((_, j) => this.board[r + i + j][c - i - j] === player)
            ) {
                return true;
            }
        }

        return false;
    }

    isWin() {
        for (let r = 0; r < this.boardSize; r++) {
            for (let c = 0; c < this.boardSize; c++) {
                if (this.board[r][c] !== 0) {
                    if (this.checkWin(r, c, this.board[r][c])) {
                        return this.board[r][c];
                    }
                }
            }
        }
        return 0;
    }

    reset() {
        this.board = Array.from({ length: this.boardSize }, () => Array(this.boardSize).fill(0));
        this.winner = 0;
    }
}

// 測試範例
// const game = new GomokuGame(15);
// game.printBoard();
