const ws = new WebSocket("ws://localhost:8765");
const chatBox = document.getElementById("chat-box");
const USER = document.getElementById("displayUsername")
const ROOMID = document.getElementById("displayRoomId")
const userNameKey = "user_name"; // 儲存使用者名字的欄位
username = sessionStorage.getItem(userNameKey);
USER.textContent = username

let player = 0;    // 預設不存在，看伺服器後決定黑或白
let winner = 2;    // 由伺服器運算，-1先手勝, 0平手, 1後手勝, 2進行中, 3未完賽
let is_myTurn = false;  // 回合
// let board = Array.from({ length: 15 }, () => Array(15).fill(0));
let board = null;
let valids = null;

function sendWhenReady(data) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
    } else {
        ws.addEventListener("open", () => {
            ws.send(data);
        }, { once: true });
    }
}

// Example usage:
document.addEventListener("DOMContentLoaded", function() {
    const message = JSON.stringify({
        action: "onloadPage",
        room_id: currentRoom,
        User: username,
        GID: GID
    });
    sendWhenReady(message);
});

window.addEventListener("beforeunload", function(event) {
    const data = JSON.stringify({
        action: "close_connection",
        room_id: currentRoom,
        sender: username
    });
    ws.send(data);
});

// 根據GID調整顯示版面
function initReplayBoard() 
{
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
    // 檢查 WebSocket 是否初始化成功
    if (ws === null) {
        console.error("WebSocket 初始化失敗！");
        return;
    }
}

//點擊處理
canvas.addEventListener("click", (event) => 
{
    if (!is_myTurn)
        return;
    if ( currentRoom ) 
    {
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
                // if (winner != 2) {
                //     ws.send(JSON.stringify({Winner: winner })); // 傳送結束條件
                // }

                const data = 
                {
                    action: "send_coordinates",
                    room_id: currentRoom,
                    sender:username,
                    Row: r,
                    Col: c,
                };

                ws.send(JSON.stringify(data)); // 傳送座標點擊資料
                is_myTurn = false;
            } else {
                console.error("WebSocket 尚未連線，無法傳送資料");
            }
        }
    }
});

async function deleteRoom(roomId) {
    try {
        // Send DELETE request to the server
        const response = await fetch(`/delete_room?room_id=${roomId}&GID=${GID}`, {
            method: 'DELETE',
        });

        // Parse the response
        const result = await response.json();

        if (result.success) {
            alert(result.message); // Notify user
            location.reload(); // Refresh the page to update the room list
        } else {
            alert(result.message); // Notify user of the error
        }
    } catch (error) {
        console.error("Error deleting room:", error);
        alert("Failed to delete the room. Please try again.");
    }
}


initReplayBoard()
drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);
let Permission = false;
// 接收訊息
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const messageElement = document.createElement("div");

    if (data.action === "get_valids") {
        valids = data["valids"]
        return;
    }

    if (data.action === "get_location") {
        Permission = true;
        is_myTurn = true;
        messageElement.textContent = `[${data.timestamp}] ${data.sender}: ${data.message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
        return;
    }

    if (data.action ==="get_board") {
        board = data.Board;
        console.log(is_myTurn)
        if (is_myTurn && valids != null) {
            valids.forEach(([row, col]) => {
                board[row][col] = 2;
            });    
        }
        drawBoard(ctx,canvas,GID,board,offset,gap,radius,len);
        return;
    }

    // 檢查是不是要顯示座標
    if(data.action === "display_location")
    {
        messageElement.textContent = `[${data.timestamp}] ${data.sender}: ${data.message["Row"]} ${data.message["Col"]}`;
    }
    else
    // 不是的話就是一般訊息
    messageElement.textContent = `[${data.timestamp}] ${data.sender}: ${data.message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
};
