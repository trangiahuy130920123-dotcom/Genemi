import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Cyber Arcade Racing 2D",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "high_score" not in st.session_state:
    st.session_state.high_score = 0

st.markdown("""
<style>
    .stApp {
        background-color: #05050a;
        color: white;
    }
    h1 {
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Courier New', Courier, monospace;
        font-size: 20px !important;
        font-weight: 900;
        margin-bottom: 0px;
    }
    .instruction {
        text-align: center;
        font-size: 11px;
        color: #00ffcc;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏎️ CYBER ARCADE RACING 2D</h1>", unsafe_allow_html=True)
st.markdown("<div class='instruction'>⚡ TỐI ƯU CHO ĐIỆN THOẠI - KHÔNG CẦN CUỘN TRANG ⚡</div>", unsafe_allow_html=True)

game_html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Cyber Arcade Racing</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #05050a;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: white;
            user-select: none;
            -webkit-user-select: none;
            overflow: hidden;
        }}
        #game-container {{
            position: relative;
            width: 100%;
            max-width: 360px;
            height: 420px;
            background: #0b0b16;
            overflow: hidden;
            border: 2px solid #00ffcc;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
            border-radius: 10px;
        }}
        canvas {{
            display: block;
            background: #0d0d1a;
            width: 100%;
            height: 100%;
        }}
        .hud {{
            position: absolute;
            top: 4px;
            left: 4px;
            right: 4px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2px;
            font-size: 10px;
            font-weight: bold;
            text-shadow: 0 0 4px #00ffcc;
            background: rgba(10, 10, 25, 0.9);
            padding: 4px;
            border-radius: 4px;
            border: 1px solid #00ffcc;
            z-index: 5;
        }}
        .hud div {{ text-align: center; }}
        .nitro-wrapper {{
            position: absolute;
            bottom: 4px;
            left: 4px;
            right: 4px;
            height: 6px;
            background: rgba(0,0,0,0.8);
            border: 1px solid #ff007f;
            border-radius: 3px;
            overflow: hidden;
            z-index: 5;
        }}
        .nitro-fill {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ff9900, #ff007f);
        }}
        .screen {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(5, 5, 10, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            z-index: 10;
        }}
        .screen h2 {{
            color: #00ffcc;
            font-size: 20px;
            margin-bottom: 8px;
            text-shadow: 0 0 10px rgba(0,255,204,0.6);
        }}
        .screen p {{
            font-size: 11px;
            margin: 4px 0 12px 0;
            padding: 0 12px;
            color: #b8c1ec;
        }}
        .btn {{
            background: linear-gradient(90deg, #00ffcc, #00bfff);
            color: #05050a;
            border: none;
            padding: 8px 20px;
            font-size: 14px;
            font-weight: 900;
            border-radius: 20px;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0,255,204,0.6);
            font-family: 'Courier New', Courier, monospace;
        }}
        .controls-pad {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            width: 100%;
            max-width: 360px;
            margin-top: 6px;
        }}
        .ctrl-btn {{
            background: #111122;
            color: #00ffcc;
            border: 1px solid #00ffcc;
            padding: 10px 0;
            font-size: 13px;
            font-weight: bold;
            border-radius: 6px;
            text-align: center;
            cursor: pointer;
            box-shadow: 0 0 5px rgba(0,255,204,0.2);
        }}
        .ctrl-btn:active {{
            background: #00ffcc;
            color: #05050a;
        }}
        .sound-toggle {{
            position: absolute;
            top: 36px;
            right: 6px;
            background: rgba(10, 10, 25, 0.9);
            border: 1px solid #00ffcc;
            color: #00ffcc;
            padding: 2px 6px;
            font-size: 9px;
            border-radius: 3px;
            cursor: pointer;
            z-index: 6;
        }}
    </style>
</head>
<body>

    <button class="sound-toggle" id="soundBtn" onclick="toggleSound()">🔊 Âm thanh</button>

    <div id="game-container">
        <canvas id="gameCanvas" width="360" height="420"></canvas>

        <div class="hud">
            <div>ĐIỂM: <span id="scoreVal">0</span></div>
            <div>TỐC ĐỘ: <span id="speedVal">100</span></div>
            <div>VÒNG: <span id="lapVal">1</span>/3</div>
            <div>CẤP: <span id="levelVal">1</span></div>
            <div>KỶ LỤC: <span id="highScoreVal">{st.session_state.high_score}</span></div>
            <div>NITRO: <span id="nitroPct">100</span>%</div>
        </div>

        <div class="nitro-wrapper">
            <div id="nitroBar" class="nitro-fill"></div>
        </div>

        <div id="startScreen" class="screen">
            <h2>CYBER RACING</h2>
            <p>Né xe địch, bứt phá Nitro và chinh phục 3 vòng đua tốc độ cao!</p>
            <button class="btn" onclick="startGame()">KHỞI ĐỘNG XE</button>
        </div>

        <div id="pauseScreen" class="screen" style="display: none;">
            <h2>TẠM DỪNG</h2>
            <button class="btn" onclick="togglePause()">TIẾP TỤC</button>
        </div>

        <div id="gameOverScreen" class="screen" style="display: none;">
            <h2 style="color: #ff007f;">VA CHẠM - GAME OVER</h2>
            <p id="finalScoreText">Điểm số: 0</p>
            <button class="btn" onclick="startGame()">THỬ LẠI</button>
        </div>

        <div id="victoryScreen" class="screen" style="display: none;">
            <h2 style="color: #ffff00;">CHIẾN THẮNG!</h2>
            <p id="victoryText">Hoàn thành xuất sắc 3 vòng đua!</p>
            <button class="btn" onclick="startGame()">ĐUA LẠI</button>
        </div>
    </div>

    <div class="controls-pad">
        <div class="ctrl-btn" ontouchstart="moveLeft(); event.preventDefault();" onclick="moveLeft()">⬅️ Trái</div>
        <div class="ctrl-btn" ontouchstart="useNitro(); event.preventDefault();" onclick="useNitro()">⚡ Nitro</div>
        <div class="ctrl-btn" ontouchstart="moveRight(); event.preventDefault();" onclick="moveRight()">➡️ Phải</div>
        <div class="ctrl-btn" ontouchstart="accelerate(); event.preventDefault();" onclick="accelerate()">⛽ Gas</div>
        <div class="ctrl-btn" ontouchstart="togglePause(); event.preventDefault();" onclick="togglePause()">⏸️ Pause</div>
        <div class="ctrl-btn" ontouchstart="brake(); event.preventDefault();" onclick="brake()">🛑 Phanh</div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        let audioCtx = null;
        let soundEnabled = true;

        function initAudio() {{
            if (!audioCtx) {{
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }}
        }}

        function toggleSound() {{
            soundEnabled = !soundEnabled;
            document.getElementById('soundBtn').innerText = soundEnabled ? "🔊 Âm thanh" : "🔇 Tắt";
        }}

        function playSound(type) {{
            if (!soundEnabled || !audioCtx) return;
            try {{
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                let now = audioCtx.currentTime;
                if (type === 'nitro') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(180, now);
                    osc.frequency.exponentialRampToValueAtTime(450, now + 0.3);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                    osc.start(now);
                    osc.stop(now + 0.3);
                }} else if (type === 'crash') {{
                    osc.type = 'square';
                    osc.frequency.setValueAtTime(90, now);
                    osc.frequency.linearRampToValueAtTime(20, now + 0.4);
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                    osc.start(now);
                    osc.stop(now + 0.4);
                }} else if (type === 'click') {{
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(600, now);
                    gain.gain.setValueAtTime(0.05, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
                    osc.start(now);
                    osc.stop(now + 0.05);
                }}
            }} catch(e) {{}}
        }}

        let gameState = 'START';
        let score = 0;
        let highScore = {st.session_state.high_score};
        let level = 1;
        let baseSpeed = 5;
        let speed = 5;
        let maxSpeed = 12;
        let nitro = 100;
        let isNitroActive = false;
        let currentLap = 1;
        let maxLaps = 3;
        let distanceCovered = 0;
        let targetDistancePerLap = 2500;
        let screenShake = 0;

        const lanes = [65, 180, 295];
        let player = {{
            lane: 1,
            x: 180,
            y: 330,
            width: 38,
            height: 70,
            color: '#00ffcc'
        }};

        let enemies = [];
        let obstacles = [];
        let roadLinesOffset = 0;
        let particles = [];
        let sideScenery = [];

        for(let i=0; i<8; i++) {{
            sideScenery.push({{ y: i * 60, side: 'left' }});
            sideScenery.push({{ y: i * 60, side: 'right' }});
        }}

        function moveLeft() {{
            initAudio();
            playSound('click');
            if (gameState === 'PLAYING' && player.lane > 0) player.lane--;
        }}

        function moveRight() {{
            initAudio();
            playSound('click');
            if (gameState === 'PLAYING' && player.lane < lanes.length - 1) player.lane++;
        }}

        function accelerate() {{
            initAudio();
            if (gameState === 'PLAYING') baseSpeed = Math.min(maxSpeed, baseSpeed + 1);
        }}

        function brake() {{
            initAudio();
            if (gameState === 'PLAYING') baseSpeed = Math.max(3, baseSpeed - 1);
        }}

        function useNitro() {{
            initAudio();
            if (gameState === 'PLAYING' && nitro > 15) {{
                isNitroActive = true;
                playSound('nitro');
                screenShake = 10;
            }}
        }}

        function togglePause() {{
            initAudio();
            playSound('click');
            if (gameState === 'PLAYING') {{
                gameState = 'PAUSED';
                document.getElementById('pauseScreen').style.display = 'flex';
            }} else if (gameState === 'PAUSED') {{
                gameState = 'PLAYING';
                document.getElementById('pauseScreen').style.display = 'none';
            }}
        }}

        function startGame() {{
            initAudio();
            playSound('click');
            gameState = 'PLAYING';
            score = 0;
            level = 1;
            baseSpeed = 5;
            speed = 5;
            nitro = 100;
            isNitroActive = false;
            currentLap = 1;
            distanceCovered = 0;
            enemies = [];
            obstacles = [];
            particles = [];
            player.lane = 1;
            player.x = lanes[1];
            screenShake = 0;

            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            document.getElementById('victoryScreen').style.display = 'none';
            document.getElementById('pauseScreen').style.display = 'none';
        }}

        function spawnEntities() {{
            // Giảm độ khó: xe địch xuất hiện thưa hơn và luôn giữ khoảng cách.
            if (Math.random() < 0.015 + (level * 0.0015)) {{
                let lane = Math.floor(Math.random() * 3);
                let safe = true;

                // Không cho xe mới xuất hiện quá gần xe khác.
                // Khoảng cách lớn giúp người chơi iPhone có thời gian né.
                for (let en of enemies) {{
                    if (en.y < 150) {{
                        safe = false;
                        break;
                    }}
                    if (en.lane === lane && en.y < 220) {{
                        safe = false;
                        break;
                    }}
                }}

                if (safe) {{
                    let colors = ['#ff007f', '#00bfff', '#ffff00', '#bf00ff'];
                    enemies.push({{
                        lane: lane,
                        x: lanes[lane],
                        y: -80,
                        width: 38,
                        height: 70,
                        speed: 1.5 + Math.random() * 1.0 + (level * 0.2),
                        color: colors[Math.floor(Math.random() * colors.length)]
                    }});
                }}
            }}
        }}

        function update() {{
            if (gameState !== 'PLAYING') return;

            if (screenShake > 0.5) screenShake *= 0.85;

            if (isNitroActive) {{
                if (nitro > 0) {{
                    speed = baseSpeed * 1.8;
                    nitro -= 0.6;
                    for (let i = 0; i < 3; i++) {{
                        particles.push({{
                            x: player.x - 12 + Math.random() * 24,
                            y: player.y + player.height,
                            vx: (Math.random() - 0.5) * 2,
                            vy: 3 + Math.random() * 3,
                            radius: 2 + Math.random() * 3,
                            color: Math.random() > 0.3 ? '#ff007f' : '#ff9900',
                            alpha: 1
                        }});
                    }}
                }} else {{
                    isNitroActive = false;
                    speed = baseSpeed;
                }}
            }} else {{
                isNitroActive = false;
                if (nitro < 100) nitro += 0.25;
                speed = baseSpeed;
            }}

            nitro = Math.max(0, Math.min(100, nitro));
            document.getElementById('nitroBar').style.width = nitro + '%';
            document.getElementById('nitroPct').innerText = Math.floor(nitro);

            let targetX = lanes[player.lane];
            player.x += (targetX - player.x) * 0.3;

            distanceCovered += speed;
            score += Math.floor(speed / 1.2);

            if (distanceCovered >= targetDistancePerLap * currentLap) {{
                if (currentLap < maxLaps) {{
                    currentLap++;
                }} else {{
                    gameState = 'VICTORY';
                    document.getElementById('victoryText').innerText = `Tổng điểm: ${{score}} - Hoàn thành 3 vòng!`;
                    document.getElementById('victoryScreen').style.display = 'flex';
                    return;
                }}
            }}

            level = Math.floor(score / 1500) + 1;
            baseSpeed = Math.min(maxSpeed, 5 + (level - 1) * 0.6);

            roadLinesOffset += speed;
            if (roadLinesOffset >= 40) roadLinesOffset = 0;

            for(let scenery of sideScenery) {{
                scenery.y += speed;
                if(scenery.y > canvas.height) scenery.y = -40;
            }}

            spawnEntities();

            for (let i = enemies.length - 1; i >= 0; i--) {{
                let en = enemies[i];
                en.y += speed - en.speed;
                en.x = lanes[en.lane];

                if (
                    player.x - player.width/2 < en.x + en.width/2 &&
                    player.x + player.width/2 > en.x - en.width/2 &&
                    player.y < en.y + en.height &&
                    player.y + player.height > en.y
                ) {{
                    triggerGameOver();
                    return;
                }}

                if (en.y > canvas.height + 70) enemies.splice(i, 1);
            }}

            for (let i = particles.length - 1; i >= 0; i--) {{
                let p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.alpha -= 0.05;
                if (p.alpha <= 0) particles.splice(i, 1);
            }}

            document.getElementById('scoreVal').innerText = score;
            document.getElementById('speedVal').innerText = Math.floor(speed * 20);
            document.getElementById('lapVal').innerText = currentLap;
            document.getElementById('levelVal').innerText = level;
        }}

        function triggerGameOver() {{
            playSound('crash');
            screenShake = 15;
            gameState = 'GAMEOVER';
            if (score > highScore) {{
                highScore = score;
                document.getElementById('highScoreVal').innerText = highScore;
            }}
            document.getElementById('finalScoreText').innerText = `Điểm số: ${{score}} | Vòng: ${{currentLap}}/3`;
            document.getElementById('gameOverScreen').style.display = 'flex';
        }}

        function drawCyberCar(x, y, width, height, mainColor, isPlayer = false) {{
            ctx.save();
            ctx.translate(x, y + height/2);

            ctx.shadowBlur = isPlayer ? 12 : 6;
            ctx.shadowColor = mainColor;

            let grad = ctx.createLinearGradient(-width/2, 0, width/2, 0);
            grad.addColorStop(0, '#111');
            grad.addColorStop(0.3, mainColor);
            grad.addColorStop(0.7, mainColor);
            grad.addColorStop(1, '#111');
            ctx.fillStyle = grad;
            ctx.fillRect(-width/2, -height/2, width, height);

            ctx.fillStyle = '#050510';
            ctx.fillRect(-width/2 + 5, -height/4, width - 10, 14);
            ctx.fillRect(-width/2 + 5, height/4 - 8, width - 10, 10);

            ctx.strokeStyle = mainColor;
            ctx.lineWidth = 1;
            ctx.strokeRect(-width/2 + 1, -height/2 + 1, width - 2, height - 2);

            ctx.fillStyle = '#000';
            ctx.fillRect(-width/2 - 4, -height/3, 5, 14);
            ctx.fillRect(width/2 - 1, -height/3, 5, 14);
            ctx.fillRect(-width/2 - 4, height/4, 5, 14);
            ctx.fillRect(width/2 - 1, height/4, 5, 14);

            ctx.fillStyle = isPlayer ? '#00ffff' : '#ff0055';
            ctx.shadowColor = isPlayer ? '#00ffff' : '#ff0055';
            ctx.shadowBlur = 8;
            ctx.fillRect(-width/2 + 3, -height/2, 6, 3);
            ctx.fillRect(width/2 - 9, -height/2, 6, 3);

            ctx.restore();
        }}

        function draw() {{
            ctx.save();
            if (screenShake > 0.5) {{
                let dx = (Math.random() - 0.5) * screenShake;
                let dy = (Math.random() - 0.5) * screenShake;
                ctx.translate(dx, dy);
            }}

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#0a0a16';
            ctx.fillRect(0, 0, 25, canvas.height);
            ctx.fillRect(335, 0, 25, canvas.height);

            ctx.fillStyle = '#ff007f';
            ctx.shadowBlur = 6;
            ctx.shadowColor = '#ff007f';
            for(let scenery of sideScenery) {{
                ctx.fillRect(12, scenery.y, 3, 12);
                ctx.fillRect(345, scenery.y, 3, 12);
            }}
            ctx.shadowBlur = 0;

            ctx.fillStyle = '#0f0f1f';
            ctx.fillRect(25, 0, 310, canvas.height);

            ctx.fillStyle = '#00ffcc';
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#00ffcc';
            ctx.fillRect(25, 0, 3, canvas.height);
            ctx.fillRect(332, 0, 3, canvas.height);
            ctx.shadowBlur = 0;

            ctx.strokeStyle = '#ff007f';
            ctx.lineWidth = 2;
            ctx.shadowBlur = 4;
            ctx.shadowColor = '#ff007f';
            ctx.setLineDash([15, 15]);
            ctx.lineDashOffset = -roadLinesOffset;

            ctx.beginPath();
            ctx.moveTo(127, 0);
            ctx.lineTo(127, canvas.height);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(233, 0);
            ctx.lineTo(233, canvas.height);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.shadowBlur = 0;

            for (let p of particles) {{
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 6;
                ctx.shadowColor = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1.0;
            }}
            ctx.shadowBlur = 0;

            for (let en of enemies) {{
                drawCyberCar(en.x, en.y, en.width, en.height, en.color, false);
            }}

            drawCyberCar(player.x, player.y, player.width, player.height, player.color, true);

            ctx.restore();
        }}

        function loop() {{
            update();
            draw();
            requestAnimationFrame(loop);
        }}

        loop();
    </script>
</body>
</html>
"""

components.html(game_html, height=600, scrolling=False)
