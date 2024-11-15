function drawBoard(ctx, canvas, game_type, board, offset, gap, radius, len) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // 繪製棋盤線條
    if(game_type==="2") //黑白棋
    {

    }
    else if(game_type==="4") //點格棋
    {
        for (let i = 0; i < board.length; i++) {
            for (let j = 0; j < board[0].length; j++) {
                const x = j * gap + offset;
                const y = i * gap + offset;
                // 根據矩陣中的值來決定繪製的內容
                if (board[i][j] === 5) {
                    // 繪製頂點
                    ctx.fillStyle = "black";
                    ctx.beginPath();
                    ctx.arc(x+gap/2, y+gap/2, radius, 0, 2 * Math.PI);
                    ctx.fill();
                } else if (board[i][j] === 0) {
                    // 繪製未選中的邊（虛線）
                    ctx.strokeStyle = "black";
                    ctx.setLineDash([5, 5]);
                    ctx.lineWidth = 3;
                    if (i % 2 === 0) {
                        // 水平線
                        ctx.beginPath();
                        ctx.moveTo(x - gap/2 + radius, y + gap/2);
                        ctx.lineTo(x + gap*3/2 - radius, y + gap/2);
                        ctx.stroke();
                    } else {
                        // 垂直線
                        ctx.beginPath();
                        ctx.moveTo(x + gap/2, y - gap/2 + radius);
                        ctx.lineTo(x + gap/2, y + gap*3/2 - radius);
                        ctx.stroke();
                    }
                } else if (board[i][j] === -1) {
                    // 繪製藍色的實線
                    ctx.strokeStyle = "blue";
                    ctx.setLineDash([]);
                    ctx.lineWidth = 5;
                    if (i % 2 === 0) {
                        // 水平線
                        ctx.beginPath();
                        ctx.moveTo(x - gap/2 + radius, y + gap/2);
                        ctx.lineTo(x + gap*3/2 - radius, y + gap/2);
                        ctx.stroke();
                    } else {
                        // 垂直線
                        ctx.beginPath();
                        ctx.moveTo(x + gap/2, y - gap/2 + radius);
                        ctx.lineTo(x + gap/2, y + gap*3/2 - radius);
                        ctx.stroke();
                    }
                } else if (board[i][j] === 1) {
                    // 繪製紅色的實線
                    ctx.strokeStyle = "red";
                    ctx.setLineDash([]);
                    ctx.lineWidth = 5;
                    if (i % 2 === 0) {
                        // 水平線
                        ctx.beginPath();
                        ctx.moveTo(x - gap/2 + radius, y + gap/2);
                        ctx.lineTo(x + gap*3/2 - radius, y + gap/2);
                        ctx.stroke();
                    } else {
                        // 垂直線
                        ctx.beginPath();
                        ctx.moveTo(x + gap/2, y - gap/2 + radius);
                        ctx.lineTo(x + gap/2, y + gap*3/2 - radius);
                        ctx.stroke();
                    }
                } else if (board[i][j] === 8) {
                    // 繪製未佔領的格子
                    // ctx.fillStyle = "#ddd"; // 灰色背景表示未佔領
                    // ctx.fillRect(x - gap / 2, y - gap / 2, gap, gap);
                } else if (board[i][j] === 7) {
                    // 繪製藍色佔領的格子
                    ctx.fillStyle = "blue";
                    ctx.fillRect(x, y, gap, gap);
                } else if (board[i][j] === 9) {
                    // 繪製紅色佔領的格子
                    ctx.fillStyle = "red";
                    ctx.fillRect(x, y, gap, gap);
                }
            }
        }
    }
    else if(game_type==="1" || game_type==="3") //圍棋&五子棋
    {
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
                radius - 2, // 內圓的半徑
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
                radius - 2, // 內圓的半徑
                x, // 外圓的 x 座標
                y, // 外圓的 y 座標
                radius // 外圓的半徑（也就是圓的大小）
            );
            gradient.addColorStop(0, "#D1D1D1");
            gradient.addColorStop(1, "#F9F9F9");
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    
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
}