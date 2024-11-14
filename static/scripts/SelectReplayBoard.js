fetch("/static/Log/Replay_log/ReplayBoard_log.json")
    .then(response => response.json())
    .then(data => {
        console.log(data)
        const boardGrid = document.getElementById("boardGrid");

        // 從 JSON 中取得每個棋盤的資訊
        data.ReplayBoards.forEach(board => {
            // 建立棋盤的按鈕或區塊
            const boardItem = document.createElement("div");
            boardItem.className = "board-item";
            
            let GameType = "";
            if(board.GID === 1)
            {
                GameType = "圍棋";
            }
            else if(board.GID === 2)
            {
                GameType = "黑白棋";
            }
            else if(board.GID === 3)
            {
                GameType = "五子棋";
            }
            else if(board.GID === 4)
            {
                GameType = "點格棋";
            }
            // 設定棋盤的顯示內容
            boardItem.innerHTML = `
                <div class="board-id">Board ID: ${board.BID}</div>
                <div class="game-id">Game : ${GameType}</div>
            `;

            // 點擊事件，用於選擇棋盤並顯示或處理相應的棋盤資訊
            boardItem.addEventListener("click", () => {
                selectBoard(board.BID, board.GID);
            });

            // 將棋盤選項加入 Grid 中
            boardGrid.appendChild(boardItem);
        });
    })
    .catch(error => console.error("無法載入 JSON 資料:", error));


function selectBoard(boardID, gameID) {
    console.log(`選擇的棋盤 ID: ${boardID}, 遊戲代號: ${gameID}`);
    // 使用 fetch 發送 POST 請求
    fetch("/SelectReplayBoard", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ BID: boardID, GID: gameID }),
    })
    .then(response => response.text())
    .then(html => {
        document.open();
        document.write(html);
        document.close();
        window.location.href = "/replayBoard";
    })
    .catch(error => console.error("Error loading board:", error));
}