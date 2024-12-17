// 獲取按鈕和輸入框元素
const loginButton = document.getElementById("login-button");
const usernameInput = document.getElementById("username");

const userNameKey = "user_name"; // 儲存使用者名字的欄位

// 按下按鈕時觸發事件
loginButton.addEventListener("click", () => {
    // 獲取輸入框中的值
    const inputUserName = usernameInput.value.trim(); // 去除多餘空格

    if (!inputUserName) {
        alert("請輸入有效的使用者名稱！");
        return; // 不繼續執行，避免空輸入
    }

    // 將值存入 sessionStorage
    sessionStorage.setItem(userNameKey, inputUserName);

    // 發送到伺服器並等待成功回應後跳轉
    saveNameToServer(inputUserName)
        .then(success => {
            if (success) {
                window.location.href = '/home'; // 成功後跳轉
            } else {
                alert("無法保存使用者名稱，請稍後再試");
            }
        });
});

// 發送使用者名稱到伺服器
async function saveNameToServer(name) {
    try {
        const response = await fetch('/save_name/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        });

        const data = await response.json();
        if (data.success) {
            return true; // 儲存成功
        } else {
            console.error('伺服器回應錯誤：', data.error);
            return false; // 儲存失敗
        }
    } catch (error) {
        console.error('發送名稱到伺服器時出錯：', error);
        return false; // 請求失敗
    }
}
