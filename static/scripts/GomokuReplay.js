//取得文件元素
const BID = document.getElementById("hiddenBID").value; //str
const GID = document.getElementById("hiddenGID").value; //str
const game_status = parseInt(document.getElementById("hiddenStatus").value, 10);
const player1 = document.getElementById("hiddenP1").value;
const player2 = document.getElementById("hiddenP2").value;
let winner = "";
if(game_status === -1)
    winner = player1;
else if(game_status === 1)
    winner = player2;

console.log(`${BID}, ${GID}, ${game_status}, ${player1}, ${player2}`)

const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
const arrow_images = document.querySelectorAll('.button-container img');    //播放圖片及箭頭圖片
const progressBar = document.getElementById("progress-bar");    //進度條
const testOutput = document.getElementById("testOutput"); // 獲取 p 標籤
testOutput.textContent = ""; // 清空 p 標籤的內容0
const game_div = document.getElementById("game");

// 固定繪製參數
let offset = 30;   //棋盤從50,50開始繪製
let len = 400;
canvas.width = len + offset*2;  // 設置畫布寬度
canvas.height = len + offset*2; // 設置畫布高度
ctx.strokeStyle = "black";  // 設置線條顏色為黑色
ctx.lineWidth = 3;         // 設置線條寬度

// 非固定繪製參數
let board = Array.from({ length: 3 }, () => Array(15).fill(0));
let gap = 0; // 每個格子的大小
let radius = 0;

let currentStep = 0;    //json list index

function initReplayBoard() 
{
    currentStep = 0;
    arrow_images.forEach((img) => {
        img.style.width = `${offset}px`; // 設置圖片的寬度
    });

    if (GID === "1")
    {
        console.log("圍棋!!!");
        board = Array.from({ length: 19 }, () => Array(19).fill(0));
        gap = len/(board[0].length-1); // 每個格子的大小
        radius = 10;
    }// 這裡應該是選擇所有的 img 元素
    else if (GID === "2")
    {
        console.log("黑白棋!!!");
    }
    else if (GID === "3")
    {
        console.log("五子棋!!!");
        board = Array.from({ length: 15 }, () => Array(15).fill(0));
        gap = len/(board[0].length-1); // 每個格子的大小
        radius = 10;
        console.log(`gap of gomoku: ${gap}`)
    }
    else if(GID === "4")
    {
        console.log("點格棋!!!");
        radius = gap/4;
        board = [
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5],
            [0, 8, 0, 8, 0, 8, 0, 8, 0],
            [5, 0, 5, 0, 5, 0, 5, 0, 5]
        ];
        radius = 10;
        gap = (len-2*offset)/(board[0].length-1); // 每個格子的大小
        console.log(`gap of dab: ${gap}`)
    }
    // 用來遍歷所有的圖片元素並修改其寬度

}

// 初次加載時選定模式繪製棋盤
initReplayBoard();
drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);

let steps = [];  // 初始時為空，之後從 JSON 載入資料
let path = "";
if(GID==="1") //圍棋
{
    path = "/static/Log/GO_log/game_log.json"; 
}
else if(GID==="2") //黑白棋
{
    path = "/static/Log/Othello_log/game_log.json";
}
else if(GID==="3") //五子棋
{
    path = "/static/Log/Gomoku_log/game_log.json";
}
else if(GID==="4") //點格棋
{
    path = "/static/Log/DaB_log/game_log.json";
}
fetch(path)
.then(response => response.json())
.then(data => {
    // console.log(data);  // 這裡打印整個 JSON 資料
    steps = data.steps;
    testOutput.textContent = "JSON 資料載入成功";
    progressBar.max = steps.length; // 設置進度條的最大值為步數的總長度
})
.catch(error => {
    testOutput.textContent = "JSON 資料載入失敗:" + error.message;
});
console.log(steps);

console.log(currentStep)
let isEnd = false;
function nextStep() {
    if (currentStep < steps.length) {
        const cur_board = steps[currentStep]["board"];
        const row = steps[currentStep]["row"];
        const col = steps[currentStep]["col"];
        const player = steps[currentStep]["player"];
        testOutput.textContent = `steps: (${row},${col}) ${currentStep+1}/${steps.length}`;
        board = cur_board;
        currentStep++;
        console.log(currentStep)
        drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);
        updateProgressBar();
    }
    else if (currentStep === steps.length) {
        if(game_status!=2 || game_status!=0) //未完成或是平手
            testOutput.textContent = `玩家 ${winner} 勝利!`;
        else if(game_status===0){
            testOutput.textContent = "平手!"
        }
        isEnd = true;
        stopAutoPlay();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        console.log(currentStep)
        const cur_board = steps[currentStep-1]["board"];
        const row = steps[currentStep]["row"];
        const col = steps[currentStep]["col"];
        const player = steps[currentStep]["player"];
        testOutput.innerHTML = `steps: <s>(${row},${col})</s> ${currentStep+1}/${steps.length}`;
        board = cur_board;
        drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);
        updateProgressBar();
    }
    else if(currentStep == 1)
    {
        currentStep--;
        console.log(currentStep)
        const row = steps[currentStep]["row"];
        const col = steps[currentStep]["col"];
        testOutput.innerHTML = `steps: <s>(${row},${col})</s> ${currentStep+1}/${steps.length}`;
        initReplayBoard();
        drawBoard(ctx, canvas, GID, board, offset, gap, radius,len)
    }
    else if(currentStep == 0)
    {
        initReplayBoard();
        drawBoard(ctx, canvas, GID, board, offset, gap, radius,len)
        testOutput.textContent = "到底了!"
    }

}

document.getElementById("right-arrow").addEventListener("click", function() {
    nextStep();
});

document.getElementById("left-arrow").addEventListener("click", function() {
    prevStep();
});

let intervalId; // 用來儲存 setInterval 的返回值
let isPlaying = false; // 用來記錄是否正在播放

function startAutoPlay() {
    if (!isPlaying) 
    {
        if(isEnd)
        {
            initReplayBoard();
            drawBoard(ctx, canvas, GID, board, offset, gap, radius,len);
            isEnd = false;
        }
        intervalId = setInterval(nextStep, 100); // 開始自動播放
        document.getElementById("auto_replay").src = "/static/images/video-pause-button.png"; // 切換為暫停圖片
        isPlaying = true;
    }
    else 
    {
        stopAutoPlay()
    }
}

function stopAutoPlay() {
    clearInterval(intervalId); // 暫停自動播放
    document.getElementById("auto_replay").src = "/static/images/play.png"; // 切換回播放圖片
    isPlaying = false;
}

// 新增點擊自動播放按鈕的事件
document.getElementById("auto_replay").addEventListener("click", function() {
    startAutoPlay();
});

function updateProgressBar() {
    // 更新進度條的位置和文字
    progressBar.value = currentStep;
}

// 進度條拖動事件處理
progressBar.addEventListener("input", function () {
    const stepValue = parseInt(progressBar.value, 10);
    currentStep = stepValue; // 更新當前步數
    console.log(`拖動進度條: 當前步數 ${currentStep}`);
    
    // 更新棋盤顯示
    if (currentStep > 0 && currentStep <= steps.length) {
        const cur_board = steps[currentStep - 1]["board"];
        board = cur_board;
        drawBoard(ctx, canvas, GID, board, offset, gap, radius, len);
        const row = steps[currentStep - 1]["row"];
        const col = steps[currentStep - 1]["col"];
        testOutput.textContent = `steps: (${row},${col}) ${currentStep}/${steps.length}`;
    } else if (currentStep === 0) {
        // 如果拖到 0，重新初始化棋盤
        initReplayBoard();
        drawBoard(ctx, canvas, GID, board, offset, gap, radius, len);
        testOutput.textContent = "到底了!";
    }
});