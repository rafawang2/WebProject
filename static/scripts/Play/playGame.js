const chatBox = document.getElementById("chat-box");
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
const GID = document.getElementById("hiddenGID").value; //str

let player = 0;    // 預設不存在，看伺服器後決定黑或白
let winner = 2;    // 由伺服器運算，-1先手勝, 0平手, 1後手勝, 2進行中, 3未完賽

// 假設這是遊戲的棋盤矩陣
board = Array.from({ length: 15 }, () => Array(15).fill(0));
const offset = 25;   //棋盤從50,50開始繪製
const gap = 50; // 每個格子的大小
const len = gap * (board[0].length-1);
const radius = 15
canvas.width = len + offset*2;  // 設置畫布寬度
canvas.height = len + offset*2; // 設置畫布高度
ctx.strokeStyle = "#2894FF";  // 設置線條顏色為黑色
ctx.lineWidth = 2;         // 設置線條寬度

// 回合
let is_myTurn = false;

// 連接到 WebSocket 伺服器
const ws = new WebSocket("ws://localhost:8765");
// const ws = new WebSocket("ws://10.106.38.184:8765");

// 初始連線時輸入用戶名稱
let username = sessionStorage.getItem("user_name");
if(!username) {
    username = prompt("Enter your name:");
}
ws.onopen = () => {
    ws.send(username); // 傳送用戶名稱到伺服器
};

// 接收來自伺服器的訊息並顯示
ws.onmessage = (event) => {
    const message = event.data;
    try {
        const parsedData = JSON.parse(message);

        if (parsedData.Winner != null) {    //伺服器廣播給所有user的勝者資料
            winner = parsedData.Winner;
            return;
        }

        if (parsedData.Board != null) {
            board = parsedData.Board;
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

        //將精準座標轉換為棋盤座標x:
        const r = Math.round((y - offset) / gap);
        const c = Math.round((x - offset) / gap);
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

// 初次加載時繪製棋盤
drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);