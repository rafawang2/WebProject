// 使用 JavaScript 載入其他 HTML
async function loadHTML() {
    try {
        const response = await fetch("/static/components/nav.html?v={{ time }}"); // 請求其他 HTML 檔案
        const htmlContent = await response.text();
        document.getElementById("nav").innerHTML = htmlContent; // 將內容插入主頁面
    } 
    catch (error) 
    {
        console.error("Error loading HTML:", error);
    }

    const headers = document.querySelectorAll('.accordion-header');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;

            // 如果內容已展開，折疊它
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                // 折疊其他展開的內容
                document.querySelectorAll('.accordion-content').forEach(c => {
                    c.style.maxHeight = null;
                });

                // 展開當前內容
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
}

// 當頁面加載完成後載入 HTML
window.onload = loadHTML;