// 獲取按鈕和輸入框元素
const loginButton = document.getElementById("login-button");
const usernameInput = document.getElementById("username");

const userNameKey = "user_name"; // 儲存使用者名字的欄位

document.addEventListener("DOMContentLoaded", function () {
    let userName = sessionStorage.getItem(userNameKey);
    console.log(`${userName}`)
    if (userName) {
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
    window.location.href = '/home'; // 成功後跳轉
});

function save_name(username) {
    fetch("/save_name", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "username": username,
        },
        body: JSON.stringify({})  // We don't need to send any data in the request body
    })
    .then(response => response.json())  // Parse the JSON response
    .then(data => {
        if (data.success) {
            console.log("Login successful")
            const UID = data.UID;
            sessionStorage.setItem("UID", UID);
        } else {
            alert("Error saving name");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while saving name.");
    });
}