async function loadHTML() {
    try {
        const response = await fetch("/static/components/nav.html?v={{ time }}"); // 請求其他 HTML 檔案
        const htmlContent = await response.text();
        document.getElementById("nav").innerHTML = htmlContent; // 將內容插入主頁面

        // 確保在 nav.html 載入完成後再進行 DOM 操作
        const userNameKey = "user_name"; // 儲存使用者名字的欄位
        let userName = sessionStorage.getItem(userNameKey);

        if (userName) {
            let user_name_elements = document.querySelectorAll(".UserName");
            user_name_elements.forEach(element => {
                element.textContent = userName; // 更新所有帶有 .UserName 類別的元素內容
            });
        }

        // 設置折疊/展開功能
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

                    const UID = sessionStorage.getItem("UID");  // 取得 UID
                    const to_profile = document.getElementById("link_to_profile");
                    to_profile.addEventListener("click", () => {
                        window.location.href = `/profile?UID=${UID}`;
                    });

                    const to_boards = document.getElementById("link_to_board_record");
                    to_boards.addEventListener("click", () => {
                        window.location.href = `/SelectReplayBoard`;
                    });
                }
            });
        });


        const UID = sessionStorage.getItem("UID"); // 從 sessionStorage 取得 UID
        const userImg = document.getElementById("user_img");

        if (UID) {
            const imageUrl = `/static/images/users/${UID}.png`;

            // 發送 HEAD 請求檢查文件是否存在
            fetch(imageUrl, { method: "HEAD" })
                .then(response => {
                    if (response.ok) {
                        userImg.src = imageUrl; // 如果存在，更新圖片位置
                    } else {
                        console.warn("User image not found, using default.");
                    }
                })
                .catch(error => {
                    console.error("Error checking user image:", error);
                });
        }

    } catch (error) {
        console.error("Error loading HTML:", error);
    }
}

// 取得使用者名稱
document.addEventListener("DOMContentLoaded", function () {
    const userNameKey = "user_name"; // 儲存使用者名字的欄位
    let userName = sessionStorage.getItem(userNameKey);
    console.log(`${userName}`)
    if (!userName) {
        window.location.href = '/login';
    }
    else {
        loadHTML();
    }
});
