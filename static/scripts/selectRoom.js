const messageInput = document.getElementById("message");
const sendButton = document.getElementById("send-button");
const chatBox = document.getElementById("chat-box");
let username = null;
let UID = sessionStorage.getItem("UID");  //取得UID，方便存資料庫UB
if(!UID)
    UID ="0800"

// 隱藏圍棋跟五子棋機器人按鈕 (尚未開發)
tobotroom_button = document.getElementById("tobotroom");
if (GID === "1" || GID === "2") {
    tobotroom_button.style.display = "none";
}
else {
    tobotroom_button.style.display = "block";
}


let exist_rooms = roomIds;

function toBotRoom() {
    window.location.href = `/bot_room?UID=${UID}&GID=${GID}`;
}

function search_room(roomId) {
    if (roomId === "") {
        show_room(exist_rooms);
    }
    else if (exist_rooms.includes(roomId)) {
        show_room([roomId]);
    }
    else {
        show_room([]);
    }
}

// 顯示room_list
function show_room(room_list) {
    console.log(exist_rooms)
    const RoomsGrid = document.getElementById("exist-room");
    RoomsGrid.innerHTML = ""; // 清空之前的內容，避免重複顯示

    room_list.forEach((roomId) => {
        const RoomItem = document.createElement("div");
        RoomItem.className = "room-item";

        // 設定房間的顯示內容
        RoomItem.innerHTML = `
            <p class="room-id">Room ID: ${roomId}</p>
        `;

        // 點擊事件，用於選擇房間
        RoomItem.addEventListener("click", () => {
            window.location.href = `/room?room_id=${roomId}&GID=${GID}`;
        });

        // 將房間選項加入 Grid 中
        RoomsGrid.appendChild(RoomItem);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    console.log("Page is fully loaded");

    const userNameKey = "user_name"; // 儲存使用者名字的欄位
    username = sessionStorage.getItem(userNameKey);

    if (!username) {
        // 如果 session 並未儲存過名字
        username = prompt("請輸入您的名字：");
        if (username) {
            sessionStorage.setItem(userNameKey, username); // 儲存到 Session Storage
        }
    }

    if(exist_rooms.length)
        show_room(exist_rooms)
    else {
        show_room([])
    }
});

function createRoom(room_id) {
    fetch("/create_room", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "room_id": room_id,
            "GID": GID
        },
        body: JSON.stringify({})  // We don't need to send any data in the request body
    })
    .then(response => response.json())  // Parse the JSON response
    .then(data => {
        if (data.success) {
            exist_rooms = data.room_ids;
            window.location.href = `/room?room_id=${room_id}&GID=${GID}`;
            show_room(exist_rooms)
        } else {
            alert("Error creating room");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while creating the room.");
    });
}