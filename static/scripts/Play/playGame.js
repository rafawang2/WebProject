const chatBox = document.getElementById("chat-box");
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
const GID = document.getElementById("hiddenGID").value; //str

let player = 0;    // 預設不存在，看伺服器後決定黑或白
let winner = 2;    // 由伺服器運算，-1先手勝, 0平手, 1後手勝, 2進行中, 3未完賽

// 假設這是遊戲的棋盤矩陣
// 固定繪製參數
let offset = 30;   //棋盤從30,30開始繪製
let len = 400;
canvas.width = len + offset*2;  // 設置畫布寬度
canvas.height = len + offset*2; // 設置畫布高度
ctx.strokeStyle = "black";  // 設置線條顏色為黑色
ctx.lineWidth = 3;         // 設置線條寬度


// 非固定繪製參數
let board = Array.from({ length: 15 }, () => Array(15).fill(0));
let gap = 0; // 每個格子的大小
let radius = 0;

// 連接到 WebSocket 伺服器
let ws = null;
// const ws = new WebSocket("ws://10.106.38.184:8765");

function initReplayBoard() 
{
    if (GID === "1")
    {
        ws = new WebSocket("ws://localhost:8764");
        console.log("圍棋!!!");
        board = Array.from({ length: 19 }, () => Array(19).fill(0));
        gap = len/(board[0].length-1); // 每個格子的大小
        radius = 10;
    }// 這裡應該是選擇所有的 img 元素
    else if (GID === "3")
    {
        ws = new WebSocket("ws://localhost:8766");
        console.log("黑白棋!!!");
        board = Array.from({ length: 10 }, () => Array(10).fill(0));
        board[5][5] = 1;
        board[4][4] = 1;
        board[4][5] = -1;
        board[5][4] = -1;
        gap = len/(board[0].length); // 每個格子的大小
        radius = 10;
    }
    else if (GID === "2")
    {
        ws = new WebSocket("ws://localhost:8765");
        console.log("五子棋!!!");
        board = Array.from({ length: 15 }, () => Array(15).fill(0));
        gap = len/(board[0].length-1); // 每個格子的大小
        radius = 10;
        console.log(`gap of gomoku: ${gap}`)
    }
    else if(GID === "4")
    {
        ws = new WebSocket("ws://localhost:8767");
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
    // 用來遍歷所有的圖片元素並修改其寬度
}

// 初次加載時繪製棋盤
initReplayBoard()
drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);

// 回合
let is_myTurn = false;

// 初始連線時輸入用戶名稱
let username = sessionStorage.getItem("user_name");
if(!username) {
    username = prompt("Enter your name:");
}
ws.onopen = () => {
    ws.send(username); // 傳送用戶名稱到伺服器
};

let valids = null;

// 接收來自伺服器的訊息並顯示
ws.onmessage = (event) => {
    const message = event.data;
    try {
        const parsedData = JSON.parse(message);

        if (parsedData.valids != null) {
            valids = parsedData.valids;
            console.log(parsedData);
            return;
        }

        if (parsedData.Winner != null) {    //伺服器廣播給所有user的勝者資料
            winner = parsedData.Winner;
            return;
        }

        if (parsedData.Board != null) {
            board = parsedData.Board;
            if (is_myTurn) {
                valids.forEach(([row, col]) => {
                    board[row][col] = 2;
                });    
            }
            drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);
            return;
        }

        if (parsedData.action === "allow") {
            is_myTurn = true;
            displayMessage(`[System] `, "Server: ", "You have permission to send coordinates!");
            return;
        }
        if (parsedData.color != null) {
            player = parsedData.color;
            return;
        }
        if (parsedData.Winner != null) {
            winner = parsedData.Winner;
            return;
        }

    } catch (e) {
        // 非 JSON 資料則繼續處理為普通訊息
    }

    // 普通訊息
    const [rawTimestamp, sender, ...contentParts] = message.split(" ");
    const timestamp = rawTimestamp.replace("[", "").replace("]", "");
    const content = contentParts.join(" ");
    displayMessage(`[${timestamp}] `, `${sender} `, content);
};

// 在畫布上按下滑鼠左鍵時傳送座標
canvas.addEventListener("mousedown", (event) => {
    if (winner != 2) {
        alert(`Game over! Winner is ${winner}  No more moves are allowed.`);
        return;
    }
    if (!is_myTurn) {
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
        if (ws.readyState === WebSocket.OPEN) {
            if (winner != 2) {
                ws.send(JSON.stringify({Winner: winner })); // 傳送結束條件
            }
            ws.send(JSON.stringify({player: player, row: r, col: c})); // 傳送座標點擊資料
            is_myTurn = false;
        } else {
            console.error("WebSocket 尚未連線，無法傳送資料");
        }
    }
});

// 顯示訊息的輔助函式
function displayMessage(timestamp, sender, content) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");

    const timestampElement = document.createElement("span");
    timestampElement.classList.add("timestamp");
    timestampElement.textContent = timestamp;

    const senderElement = document.createElement("span");
    senderElement.classList.add("sender");
    senderElement.textContent = sender;

    const contentElement = document.createElement("span");
    contentElement.classList.add("content");
    contentElement.textContent = content;

    messageElement.appendChild(timestampElement);
    messageElement.appendChild(senderElement);
    messageElement.appendChild(contentElement);

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 滾動到底部
}