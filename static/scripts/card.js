// 定義每個遊戲的資料
const games = [
    { name: "圍棋", image: "/static/images/tools/GO.jpg", description: "點擊以遊玩" ,GID:"1"},
    { name: "五子棋", image: "/static/images/tools/5.jpg", description: "點擊以遊玩" ,GID:"2"},
    { name: "黑白棋", image: "/static/images/tools/othello.jpg", description: "點擊以遊玩",GID:"3" },
    { name: "點格棋", image: "/static/images/tools/D&B.jpg", description: "點擊以遊玩",GID:"4" }
];

// 取得主容器元素
const container = document.getElementById('gameContainer');

// 使用迴圈生成每個遊戲的卡片
games.forEach(game => 
{
    // 建立卡片的外層 button
    const cardBtn = document.createElement('button');
    cardBtn.className = 'card';
    cardBtn.id = game.GID
    // 建立卡片內容區域
    const contentDiv = document.createElement('div');
    contentDiv.className = 'content';

    // 建立圖片區域
    const imgDiv = document.createElement('div');
    imgDiv.className = 'img';
    const img = document.createElement('img');
    img.src = game.image;
    img.alt = game.name; // 設定圖片的 alt 屬性
    imgDiv.appendChild(img);

    // 建立文字內容區域
    const cardContentDiv = document.createElement('div');
    cardContentDiv.className = 'cardContent';
    const title = document.createElement('h3');
    title.innerHTML = `${game.name}<br><span>${game.description}</span>`;

    // 組合結構
    cardContentDiv.appendChild(title);
    contentDiv.appendChild(imgDiv);
    contentDiv.appendChild(cardContentDiv);
    cardBtn.appendChild(contentDiv);
    container.appendChild(cardBtn);
});

const buttons = document.querySelectorAll('.card');

// 為每個按鈕綁定 click 事件
buttons.forEach((button) => 
{
    button.addEventListener('click', () => 
    {
        switch (button.id) 
        {
            case '1':
                alert('開啟圍棋遊戲');
                // 這裡可以添加對應的遊戲功能，例如跳轉到其他頁面
                // window.location.href = /playGame?GID=1';
                break;

            case '2':
                // alert('開啟五子棋遊戲');
                window.location.href = '/playGame?GID=2';
                break;

            case '3':
                alert('開啟黑白棋遊戲');
                // window.location.href = '/playGame?GID=3';
                break;

            case '4':
                alert('開啟點格棋遊戲');
                // window.location.href = '/playGame?GID=3';
                break;

            default:
                console.warn('未定義的遊戲');
        }
    });
});
