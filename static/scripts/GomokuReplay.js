const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
// 假設這是遊戲的棋盤矩陣
const board = Array.from({ length: 15 }, () => Array(15).fill(0));
const offset = 25;   //棋盤從50,50開始繪製
const gap = 50; // 每個格子的大小
const len = gap * (board[0].length-1);
const radius = 15
canvas.width = len + offset*2;  // 設置畫布寬度
canvas.height = len + offset*2; // 設置畫布高度
ctx.strokeStyle = "black";  // 設置線條顏色為黑色
ctx.lineWidth = 3;         // 設置線條寬度

const testOutput = document.getElementById("testOutput"); // 獲取 p 標籤
testOutput.textContent = ""; // 清空 p 標籤的內容0

function drawBlack(i, j) {
    let x = offset + gap * j;
    let y = offset + gap * i;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.closePath();

    // 設定漸層，並用固定半徑來設定
    var gradient = ctx.createRadialGradient(
        x, // 內圓的 x 座標
        y, // 內圓的 y 座標
        13, // 內圓的半徑
        x, // 外圓的 x 座標
        y, // 外圓的 y 座標
        radius // 外圓的半徑（也就是圓的大小）
    );

    gradient.addColorStop(0, "#0a0a0a"); // 內圓顏色
    gradient.addColorStop(1, "#636766"); // 外圓顏色
    ctx.fillStyle = gradient;
    ctx.fill();
}

function drawWhite(i,j){
    let x = offset + gap*j
    let y = offset + gap*i
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.closePath();
    // 設定漸層，並用固定半徑來設定
    var gradient = ctx.createRadialGradient(
        x, // 內圓的 x 座標
        y, // 內圓的 y 座標
        13, // 內圓的半徑
        x, // 外圓的 x 座標
        y, // 外圓的 y 座標
        radius // 外圓的半徑（也就是圓的大小）
    );
    gradient.addColorStop(0, "#D1D1D1");
    gradient.addColorStop(1, "#F9F9F9");
    ctx.fillStyle = gradient;
    ctx.fill();
}

function drawBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // 繪製棋盤線條
    for (let i = 0; i < board[0].length; i++) {
        const y = offset + i * gap;
        ctx.beginPath();
        ctx.moveTo(offset, y);
        ctx.lineTo(offset + len, y);
        ctx.stroke();

        const x = offset + i * gap;
        ctx.beginPath();
        ctx.moveTo(x, offset);
        ctx.lineTo(x, offset + len);
        ctx.stroke();
    }
    for (let i = 0; i < board[0].length; i++) {
        for (let j = 0; j < board[0].length; j++) {
            if(board[i][j]===-1)
                drawBlack(i,j)
            else if(board[i][j]===1)
                drawWhite(i,j)
        }
    }
}

const game_div = document.getElementById("game");
// game_div.style.width = (canvas.width + offset) + "px";
// game_div.style.height = (canvas.height + offset) + "px";

// 初次加載時繪製棋盤
drawBoard();



let steps = [];  // 初始時為空，之後從 JSON 載入資料
fetch("/static/Log/Gomoku_log/game_log.json")
    .then(response => response.json())
    .then(data => {
        console.log(data);  // 這裡打印整個 JSON 資料
        steps = data.steps;
        testOutput.textContent = "JSON 資料載入成功";
    })
    .catch(error => {
        testOutput.textContent = "JSON 資料載入失敗:" + error.message;
    });

let currentStep = 0;
let lastPlayer = null; // 儲存最後一次的玩家

function nextStep() {
    if (currentStep < steps.length) {
        const { x, y, player } = steps[currentStep];
        testOutput.textContent = `steps: (${x},${y}) ${currentStep+1}/${steps.length}`;
        board[x][y] = player;
        lastPlayer = player; // 更新最後的玩家
        currentStep++;
        drawBoard();
    }
    else if (currentStep === steps.length) {
        testOutput.textContent = `玩家${lastPlayer}勝利!`; // 使用最後的玩家
    }
}

function prevStep() {
    if (currentStep > 0) {
        currentStep--;
        const { x, y } = steps[currentStep];
        testOutput.innerHTML = `steps: <s>(${x},${y})</s> ${currentStep+1}/${steps.length}`;
        board[x][y] = 0;
        drawBoard();
        
    }
    else if(currentStep == 0)
    {
        testOutput.textContent = "到底了!"
    }

}

document.getElementById("right-arrow").addEventListener("click", function() {
    nextStep();
});

document.getElementById("left-arrow").addEventListener("click", function() {
    prevStep();
});