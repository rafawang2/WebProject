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
    console.log(inputUserName)
    window.location.href = '/home'; // 成功後跳轉
});
