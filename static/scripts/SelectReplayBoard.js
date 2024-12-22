// 獲取使用者的 UID
let UID = sessionStorage.getItem("UID");

// 調用 API
fetch("/get_replay_BIDs", {
    method: "GET",
    headers: {
        "Content-Type": "application/json",
        "UID": UID // 將 UID 傳遞到伺服器
    }
})
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json(); // 將 API 返回的響應解析為 JSON
    })
    .then(data => {
        console.log("BIDs:", data); // 在控制台查看返回的 BIDs 資料

        const boardGrid = document.getElementById("boardGrid");

        // 遍歷 API 返回的 JSON 資料
        Object.entries(data).forEach(([bid, board]) => {
            // 建立棋盤的按鈕或區塊
            const boardItem = document.createElement("div");
            boardItem.className = "board-item";

            // 確定遊戲類型
            let GameType = "";
            if (board.GID === 1) {
                GameType = "圍棋";
            } else if (board.GID === 2) {
                GameType = "五子棋";
            } else if (board.GID === 3) {
                GameType = "黑白棋";
            } else if (board.GID === 4) {
                GameType = "點格棋";
            }

            // 確定勝利者
            let winner = "";
            if (board.state === -1) {
                winner = board.player1;
            } else if (board.state === 1) {
                winner = board.player2;
            } else {
                winner = "Tie";
            }

            // 設定棋盤的顯示內容
            boardItem.innerHTML = `
                <p class="board-id">Board ID: ${bid}</p>
                <p class="game-id">Game: ${GameType}</p>
                <p class="VS">${board.player1} VS ${board.player2}</p>
                <p class="winner">Winner: ${winner}</p>
            `;

            // 點擊事件，用於選擇棋盤並顯示或處理相應的棋盤資訊
            boardItem.addEventListener("click", () => {
                selectBoard(bid, UID, board.state, board.player1, board.player2);
            });

            // 將棋盤選項加入 Grid 中
            boardGrid.appendChild(boardItem);
        });
    })
    .catch(error => {
        console.error("There was a problem with the fetch operation:", error);
    });


// fetch("/static/Log/Replay_log/ReplayBoard_log.json")
//     .then(response => response.json())
//     .then(data => {
//         console.log(data);
//         const boardGrid = document.getElementById("boardGrid");
        
//         // 從 JSON 中取得所有棋盤的資訊 (改為 Object.entries 來遍歷鍵值對)
//         Object.entries(data.ReplayBoards).forEach(([bid, board]) => {
//             // 建立棋盤的按鈕或區塊
//             const boardItem = document.createElement("div");
//             boardItem.className = "board-item";

//             let GameType = "";
//             if (board.GID === 1) {
//                 GameType = "圍棋";
//             } else if (board.GID === 2) {
//                 GameType = "五子棋";
//             } else if (board.GID === 3) {
//                 GameType = "黑白棋";
//             } else if (board.GID === 4) {
//                 GameType = "點格棋";
//             }

//             let winner = "";
//             console.log(board.status);
//             if (board.status === -1)
//                 winner = board.player1;
//             else if (board.status === 1)
//                 winner = board.player2;
//             else
//                 winner = "Tie";

//             // 設定棋盤的顯示內容
//             boardItem.innerHTML = `
//                 <p class="board-id">Board ID: ${bid}</p>
//                 <p class="game-id">Game : ${GameType}</p>
//                 <p class="VS">${board.player1} VS ${board.player2}</p>
//                 <p class="winner">Winner: ${winner}</p>
//             `;

//             // 點擊事件，用於選擇棋盤並顯示或處理相應的棋盤資訊
//             boardItem.addEventListener("click", () => {
//                 selectBoard(bid, board.GID, board.status, board.player1, board.player2);
//             });

//             // 將棋盤選項加入 Grid 中
//             boardGrid.appendChild(boardItem);
//         });
//     })
//     .catch(error => console.error("無法載入 JSON 資料:", error));

function selectBoard(boardID, userID, status, p1, p2) {
    console.log(`選擇的棋盤 ID: ${boardID}, User ID: ${userID}, 遊戲狀態: ${status}, 玩家1: ${p1}, 玩家2: ${p2}`);
    window.location.href = `/SelectReplayBoard/replayBoard?BID=${boardID}&UID=${userID}`;
}
