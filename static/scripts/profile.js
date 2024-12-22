document.getElementById("upload_button").addEventListener("click", function() {
    // 當按鈕被點擊時，觸發隱藏的 <input> 文件選擇框
    document.getElementById("file_input").click();
});

//取得用戶的圖片輸入
document.getElementById("file_input").addEventListener("change", function(event) {
    const file = event.target.files[0]; // 獲取選擇的文件(只取第一個檔案)
    if (file) {
        const formData = new FormData();
        formData.append('image', file); // 將圖片附加到表單數據

        // 使用 fetch 發送圖片到 FastAPI 伺服器
        fetch('/upload/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => { //data為伺服器返回的json字串{"success": True, "image_url": f"/static/images/users/man.png"}
            if (data.success) {
                // 更新頁面顯示上傳後的圖片
                const timestamp = new Date().getTime(); // 獲取當前時間戳
                document.getElementById("user_img").src = `${data.image_url}?t=${timestamp}`;
                location.reload(); // 這裡重新加載頁面
            } else {
                alert('上傳失敗');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('上傳錯誤');
        });
    }
});

const UID = sessionStorage.getItem("UID");  // 取得 UID
const url = `/static/Log/GameRecord_log/Record_${UID}.json`;  // 生成 URL
console.log(url);  // 記錄 URL

// 取得玩家的遊戲紀錄
fetch(url)
    .then(response => response.json())
    .then(data => {
        const Record_container = document.getElementById("game_record_container");
        
        // 從 JSON 中取得所有棋盤的資訊 (改為 Object.entries 來遍歷鍵值對)
        Object.entries(data.record).forEach(([GID, board]) => {
            const boardItem = document.createElement("div");
            boardItem.className = "game-record";

            let GameType = "";
            if (GID === "1") {
                GameType = "圍棋";
            } else if (GID === "2") {
                GameType = "黑白棋";
            } else if (GID === "3") {
                GameType = "五子棋";
            } else if (GID === "4") {
                GameType = "點格棋";
            }

            boardItem.innerHTML = `
                <h3>${GameType}</h3>
                <p>總場數：${board.total}</p>
                <p>勝場：${board.win}</p>
                <p>敗場：${board.lose}</p>
            `;
            Record_container.appendChild(boardItem);
        });
    })
    .catch(error => console.error("無法載入 JSON 資料:", error));
