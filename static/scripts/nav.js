// 使用 JavaScript 載入其他 HTML
async function loadHTML() {
    try {
        const response = await fetch("/static/components/nav.html"); // 請求其他 HTML 檔案
        const htmlContent = await response.text();
        document.getElementById("nav").innerHTML = htmlContent; // 將內容插入主頁面
    } 
    catch (error) 
    {
        console.error("Error loading HTML:", error);
    }
}

// 當頁面加載完成後載入 HTML
window.onload = loadHTML;