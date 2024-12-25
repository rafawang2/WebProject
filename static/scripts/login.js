// 獲取按鈕和輸入框元素
const loginButton = document.getElementById("login-button");
const usernameInput = document.getElementById("username");

const userNameKey = "user_name"; // 儲存使用者名字的欄位

document.addEventListener("DOMContentLoaded", function () {
    let userName = sessionStorage.getItem(userNameKey);
    let UID = sessionStorage.getItem("UID");
    console.log(`${userName}`)
    if (userName && UID) {
        window.location.href = '/home';
    }
});

// 按下按鈕時觸發事件
loginButton.addEventListener("click", () => {
    console.log("click!")
    // 獲取輸入框中的值
    const inputUserName = usernameInput.value;

    if (!inputUserName) {
        alert("請輸入有效的使用者名稱！");
        return; // 不繼續執行，避免空輸入
    }

    // 檢查使用者名稱是否超過10個字元
    if (inputUserName.length > 10) {
        alert("使用者名稱不可超過 10 個字元！");
        return; // 不繼續執行
    }

    // 將值存入 sessionStorage
    sessionStorage.setItem(userNameKey, inputUserName);
    save_name(inputUserName)
    console.log(inputUserName)
});

async function save_name(username) {
    await fetch("/save_name", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "username": username
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json()
    })
    .then(data => {
        console.log("Response data:", data); // 確認收到的數據
        const UID = data.UID;
        sessionStorage.setItem("UID", UID);
        if(!UID)
            window.location.href = '/login';
        else
            window.location.href = '/home'
        
    })
    .catch(error => {
        console.error("Error occurred during fetch:", error);
        alert("An error occurred while saving name.");
    });
}