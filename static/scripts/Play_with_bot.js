const chatBox = document.getElementById("chat-box");
const messageContainer = document.getElementById("message-container");
const playerContainer = document.getElementById("players-container");
const player1Element = document.getElementById("player1");
const player2Element = document.getElementById("player2");
const userNameKey = "user_name"; // 儲存使用者名字的欄位
username = sessionStorage.getItem(userNameKey);
let UID = sessionStorage.getItem("UID");  //取得UID，方便存資料庫UB
if(!UID)
    UID ="0800"

let players = null;

// 設定 chatBox 高度
chatBox.style.minHeight = (len + offset * 2) + 'px';
chatBox.style.maxHeight = (len + offset * 2) + 'px';

// 將高度數值轉為數字
const chatBoxHeight = len + offset * 2; // 這是數值，無需解析

// 設定 messageContainer 高度
const messageContainerHeight = chatBoxHeight * 0.85;
messageContainer.style.minHeight = messageContainerHeight + 'px';
messageContainer.style.maxHeight = messageContainerHeight + 'px';

// 設定 playerContainer 高度
const playerContainerHeight = chatBoxHeight * 0.15;
playerContainer.style.minHeight = playerContainerHeight + 'px';
playerContainer.style.maxHeight = playerContainerHeight + 'px';



let player = 0;    // 預設不存在，看伺服器後決定黑或白
let winner = 2;    // 由伺服器運算，-1先手勝, 0平手, 1後手勝, 2進行中, 3未完賽
let is_myTurn = true;  // 預設玩家先手
// let board = Array.from({ length: 15 }, () => Array(15).fill(0));
let valids = null;

// 載入
document.addEventListener("DOMContentLoaded", function() {
    initReplayBoard();
    drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
    fetch(`/get_board?UID=${UID}&GID=${GID}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json(); // 將 API 返回的響應解析為 JSON
    })
    .then(data => {
        console.log(data)
        if (data.winner != 2) {
            if (winner === -1) {
                player1Element.classList.add('winner');
                player2Element.classList.remove('winner');
            }
            else if (winner === 0) {
                player1Element.classList.add('winner');
                player2Element.classList.add('winner');
            }
            else if (winner === 1) {
                player1Element.classList.remove('winner');
                player2Element.classList.add('winner');
            }
            is_myTurn = false; // 遊戲結束，禁止點擊
            board = data.board;
            winner = data.winner;
            drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
            msg = {
                "sender": "Server",
                "message": `${winner} won`
            }
            displayMSG(msg)
        }
        else {
            // 正確設置 board
            board = data.board;
            if (is_myTurn && valids != null && GID==="3") {
                valids.forEach(([row, col]) => {
                    board[row][col] = 2;
                });    
            }
            // 繪製棋盤的函數應在數據獲取後執行
            drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
        }
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
});


// 離開
window.addEventListener("beforeunload", function(event) {
    const data = JSON.stringify({
        action: "close_connection",
    });
});

// 根據GID調整顯示版面
function initReplayBoard() 
{
    player1Element.textContent = username;
    player2Element.textContent = "BOT";

    if (GID === "1")
    {
        console.log("圍棋!!!");
        board = Array.from({ length: 19 }, () => Array(19).fill(0));
        gap = len/(board[0].length-1); // 每個格子的大小
        radius = 10;
    }// 這裡應該是選擇所有的 img 元素
    else if (GID === "3")
    {
        console.log("黑白棋!!!");
        board = Array.from({ length: 8 }, () => Array(8).fill(0));
        board[4][4] = 1;
        board[3][3] = 1;
        board[3][4] = -1;
        board[4][3] = -1;
        gap = len/(board[0].length); // 每個格子的大小
        radius = 20;
    }
    else if (GID === "2")
    {
        console.log("五子棋!!!");
        board = Array.from({ length: 15 }, () => Array(15).fill(0));
        gap = len/(board[0].length-1); // 每個格子的大小
        radius = 10;
        console.log(`gap of gomoku: ${gap}`)
    }
    else if(GID === "4")
    {
        console.log("點格棋!!!");
        radius = gap/4;
        board = [
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5]
        ];
        radius = 10;
        gap = (len-2*offset)/(board[0].length-1); // 每個格子的大小
        console.log(`gap of dab: ${gap}`)
        console.log(board);
    }
}

function handleClick(row, col) {
    // 發送座標到伺服器
    msg = {
        "sender": username,
        "message": `${row} ${col}`
    }
    displayMSG(msg)
    is_myTurn = false; //先關閉等待伺服器回應
    fetch(`/user_send_coordinate?UID=${UID}`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "row": row,
            "col": col
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.winner != 2) {
            is_myTurn = false; // 遊戲結束，禁止點擊
            board = data.board;
            winner = data.winner;
            if (winner === -1) {
                player1Element.classList.add('winner');
                player2Element.classList.remove('winner');
            }
            else if (winner === 0) {
                player1Element.classList.add('winner');
                player2Element.classList.add('winner');
            }
            else if (winner === 1) {
                player1Element.classList.remove('winner');
                player2Element.classList.add('winner');
            }
            drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面

            msg = {
                "sender": "Server",
                "message": `${winner} won`
            }
            displayMSG(msg)
        } 
        else {
            // 伺服器返回新的 board，更新顯示
            board = data.board;
            drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
            
            if(data.permission === "Human") {
                setTimeout(() => {
                    // 這裡可以確保更新過後的效果
                    player1Element.classList.add('current-player');
                    player2Element.classList.remove('current-player');
                }, 0); // 延遲 0 毫秒強制重繪
                msg = {
                    "sender": "Server",
                    "message": `Your turn`
                };

                is_myTurn = true;
                valids = data.valid_moves;
                if(is_myTurn && valids != null && GID==="3") {
                    valids.forEach(([row, col]) => {
                        board[row][col] = 2;
                    });
                }
                console.log(valids)
                drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
            }
            else if (data.permission === "BOT") {
                setTimeout(() => {
                    // 這裡可以確保更新過後的效果
                    player1Element.classList.remove('current-player');
                    player2Element.classList.add('current-player');
                }, 0); // 延遲 0 毫秒強制重繪
                msg = {
                    "sender": "Server",
                    "message": `Bot's turn`
                };
                is_myTurn = false;
                get_bot_move();
                drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function get_bot_move() {
    fetch(`/get_bot_move?UID=${UID}&GID=${GID}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        }
    })
    .then(response => response.json())
    .then(data => {

        if (data.winner != 2) {
            is_myTurn = false; // 遊戲結束，禁止點擊
            board = data.board;
            winner = data.winner;
            if (winner === -1) {
                player1Element.classList.add('winner');
                player2Element.classList.remove('winner');
            }
            else if (winner === 0) {
                player1Element.classList.add('winner');
                player2Element.classList.add('winner');
            }
            else if (winner === 1) {
                player1Element.classList.remove('winner');
                player2Element.classList.add('winner');
            }
            drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面

            msg = {
                "sender": "Server",
                "message": `${winner} won`
            }
            displayMSG(msg)
        }
        else {
            // 正確設置 board
            board = data.board;
            msg = data.message;
            displayMSG(msg);
            // 繪製棋盤的函數應在數據獲取後執行
            drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
            if(data.permission === "Human") {
                setTimeout(() => {
                    // 這裡可以確保更新過後的效果
                    player1Element.classList.add('current-player');
                    player2Element.classList.remove('current-player');
                }, 0); // 延遲 0 毫秒強制重繪

                msg = {
                    "sender": "Server",
                    "message": `Your turn`
                };

                is_myTurn = true;
                valids = data.valid_moves;
                if(is_myTurn && valids != null && GID==="3") {
                    valids.forEach(([row, col]) => {
                        board[row][col] = 2;
                    });
                }
                drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
            }
            else if (data.permission === "BOT") {
                setTimeout(() => {
                    // 這裡可以確保更新過後的效果
                    player1Element.classList.remove('current-player');
                    player2Element.classList.add('current-player');
                }, 0); // 延遲 0 毫秒強制重繪
                msg = {
                    "sender": "Server",
                    "message": `Bot's turn`
                };
                is_myTurn = false;
                drawBoard(ctx, canvas, GID, board, offset, gap, radius, len); // 更新棋盤畫面
                get_bot_move();
            }
        }
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });
}


//點擊處理
canvas.addEventListener("click", (event) => 
{   
    if (!is_myTurn){
        return;
    }
    if (event.button === 0) { // 左鍵
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        let r = -1;
        let c = -1;
        //將精準座標轉換為棋盤座標x:
        if (GID === "1" || GID === "2") {
            r = Math.round((y - offset) / gap);
            c = Math.round((x - offset) / gap);
        }
        else {
            r = Math.floor((y - offset) / gap);
            c = Math.floor((x - offset) / gap);
        }
        // sendCoordinate(r, c)
        handleClick(r,c)
    }
});


function displayMSG(data) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.textContent = ` ${data.sender}: ${data.message}`;
    messageContainer.appendChild(messageElement);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}