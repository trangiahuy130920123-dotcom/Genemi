import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Retro Arcade Racing 2D",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "high_score" not in st.session_state:
    st.session_state.high_score = 0

st.markdown("""
<style>
.stApp { background-color:#0d1117; color:white; }
h1 { text-align:center; color:#00ffcc; font-family:'Courier New',Courier,monospace;
text-shadow:0 0 10px rgba(0,255,204,.5); }
.instruction { text-align:center; font-size:13px; color:#8b949e; margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏎️ RETRO ARCADE RACING 2D</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='instruction'>Dùng phím mũi tên hoặc bảng điều khiển bên dưới. "
    "Nhấn Space hoặc Nitro để bứt tốc!</div>",
    unsafe_allow_html=True
)

game_html = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
*{box-sizing:border-box}
body{margin:0;padding:0;background:#0d1117;font-family:'Courier New',monospace;
display:flex;flex-direction:column;align-items:center;color:white;user-select:none}
#game-container{position:relative;width:100%;max-width:380px;height:560px;background:#161b22;
overflow:hidden;border:3px solid #00ffcc;box-shadow:0 0 25px rgba(0,255,204,.3);border-radius:12px}
canvas{display:block;background:#21262d;width:100%;height:100%;touch-action:none}
.hud{position:absolute;top:8px;left:8px;right:8px;display:grid;grid-template-columns:repeat(3,1fr);
gap:4px;font-size:11px;font-weight:bold;text-shadow:1px 1px #000;pointer-events:none;
background:rgba(0,0,0,.6);padding:6px;border-radius:6px;border:1px solid #30363d}
.hud div{text-align:center}
.nitro-wrapper{position:absolute;bottom:8px;left:8px;right:8px;height:10px;background:rgba(0,0,0,.7);
border:1px solid #8b949e;border-radius:5px;overflow:hidden;pointer-events:none}
.nitro-fill{width:100%;height:100%;background:linear-gradient(90deg,#ff9900,#ff3300)}
.screen{position:absolute;inset:0;background:rgba(13,17,23,.92);display:flex;
flex-direction:column;justify-content:center;align-items:center;text-align:center;z-index:10}
.screen h2{color:#00ffcc;font-size:24px;margin-bottom:8px}
.screen p{font-size:13px;margin:4px 0 15px;padding:0 15px;color:#c9d1d9}
.btn{background:#00ffcc;color:#0d1117;border:0;padding:10px 24px;font-size:15px;
font-weight:bold;border-radius:20px;cursor:pointer;box-shadow:0 4px #00aa88;font-family:inherit}
.btn:active{transform:translateY(3px);box-shadow:0 1px #00aa88}
.controls-pad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;width:100%;
max-width:380px;margin-top:10px}
.ctrl-btn{background:#21262d;color:#00ffcc;border:2px solid #30363d;padding:12px 0;font-size:15px;
font-weight:bold;border-radius:8px;text-align:center;cursor:pointer;box-shadow:0 3px #111}
.ctrl-btn:active{background:#00ffcc;color:#0d1117;transform:translateY(2px)}
.sound-toggle{position:absolute;top:55px;right:12px;background:rgba(0,0,0,.6);
border:1px solid #30363d;color:white;padding:4px 8px;font-size:11px;border-radius:4px;cursor:pointer;z-index:5}
</style>
</head>
<body>
<div id="game-container">
<button class="sound-toggle" id="soundBtn" onclick="toggleSound()">🔊 Âm thanh: BẬT</button>
<canvas id="gameCanvas" width="380" height="560"></canvas>

<div class="hud">
<div>ĐIỂM: <span id="scoreVal">0</span></div>
<div>TỐC ĐỘ: <span id="speedVal">100</span> km/h</div>
<div>VÒNG: <span id="lapVal">1</span>/3</div>
<div>CẤP: <span id="levelVal">1</span></div>
<div>KỶ LỤC: <span id="highScoreVal">0</span></div>
<div>NITRO: <span id="nitroPct">100</span>%</div>
</div>
<div class="nitro-wrapper"><div id="nitroBar" class="nitro-fill"></div></div>

<div id="startScreen" class="screen">
<h2>RETRO RACING</h2>
<p>Né xe địch, thu thập điểm, dùng Nitro và hoàn thành 3 vòng đua!</p>
<button class="btn" onclick="startGame()">BẮT ĐẦU NGAY</button>
</div>

<div id="pauseScreen" class="screen" style="display:none">
<h2>TẠM DỪNG</h2><button class="btn" onclick="togglePause()">TIẾP TỤC</button>
</div>

<div id="gameOverScreen" class="screen" style="display:none">
<h2 style="color:#ff5555">GAME OVER</h2>
<p id="finalScoreText">Điểm số: 0</p>
<button class="btn" onclick="startGame()">CHƠI LẠI</button>
</div>

<div id="victoryScreen" class="screen" style="display:none">
<h2 style="color:#f1e05a">CHIẾN THẮNG!</h2>
<p id="victoryText">Bạn đã hoàn thành 3 vòng đua!</p>
<button class="btn" onclick="startGame()">ĐUA LẠI</button>
</div>
</div>

<div class="controls-pad">
<div class="ctrl-btn" onclick="moveLeft()">⬅️ Trái</div>
<div class="ctrl-btn" onclick="useNitro()">⚡ Nitro</div>
<div class="ctrl-btn" onclick="moveRight()">➡️ Phải</div>
<div class="ctrl-btn" onpointerdown="startAccelerate()" onpointerup="stopAccelerate()">⛽ Gas</div>
<div class="ctrl-btn" onclick="togglePause()">⏸️ Pause</div>
<div class="ctrl-btn" onpointerdown="startBrake()" onpointerup="stopBrake()">🛑 Phanh</div>
</div>

<script>
const canvas=document.getElementById('gameCanvas');
const ctx=canvas.getContext('2d');
const lanes=[75,190,305];
let audioCtx=null,soundEnabled=true;
let gameState='START',score=0,highScore=0,level=1;
let baseSpeed=4.5,speed=4.5,maxSpeed=11,nitro=100;
let isNitroActive=false,currentLap=1,maxLaps=3,distanceCovered=0;
const targetDistancePerLap=2500;
let player={lane:1,x:190,y:440,width:40,height:75,color:'#ff3366'};
let enemies=[],obstacles=[],roadLinesOffset=0,particles=[];
let accelerateHeld=false,brakeHeld=false;

function initAudio(){if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)()}
function toggleSound(){
 soundEnabled=!soundEnabled;
 document.getElementById('soundBtn').innerText=soundEnabled?'🔊 Âm thanh: BẬT':'🔇 Âm thanh: TẮT';
}
function playSound(type){
 if(!soundEnabled)return; initAudio();
 try{
  let o=audioCtx.createOscillator(),g=audioCtx.createGain();o.connect(g);g.connect(audioCtx.destination);
  let n=audioCtx.currentTime;
  if(type==='nitro'){o.type='sawtooth';o.frequency.setValueAtTime(150,n);
   o.frequency.exponentialRampToValueAtTime(400,n+.3);g.gain.setValueAtTime(.2,n);
   g.gain.exponentialRampToValueAtTime(.01,n+.3);o.start();o.stop(n+.3)}
  else if(type==='crash'){o.type='square';o.frequency.setValueAtTime(80,n);
   o.frequency.linearRampToValueAtTime(30,n+.4);g.gain.setValueAtTime(.3,n);
   g.gain.exponentialRampToValueAtTime(.01,n+.4);o.start();o.stop(n+.4)}
  else{o.type='sine';o.frequency.setValueAtTime(600,n);g.gain.setValueAtTime(.1,n);
   g.gain.exponentialRampToValueAtTime(.01,n+.08);o.start();o.stop(n+.08)}
 }catch(e){}
}
function moveLeft(){initAudio();playSound('click');if(gameState==='PLAYING'&&player.lane>0)player.lane--}
function moveRight(){initAudio();playSound('click');if(gameState==='PLAYING'&&player.lane<2)player.lane++}
function accelerate(){if(gameState==='PLAYING')baseSpeed=Math.min(maxSpeed,baseSpeed+.5)}
function brake(){if(gameState==='PLAYING')baseSpeed=Math.max(2.5,baseSpeed-.7)}
function startAccelerate(){accelerateHeld=true;accelerate()}
function stopAccelerate(){accelerateHeld=false}
function startBrake(){brakeHeld=true;brake()}
function stopBrake(){brakeHeld=false}
function useNitro(){initAudio();if(gameState==='PLAYING'&&nitro>15){isNitroActive=true;playSound('nitro')}}
function togglePause(){
 initAudio();playSound('click');
 if(gameState==='PLAYING'){gameState='PAUSED';document.getElementById('pauseScreen').style.display='flex'}
 else if(gameState==='PAUSED'){gameState='PLAYING';document.getElementById('pauseScreen').style.display='none'}
}
function startGame(){
 initAudio();playSound('click');gameState='PLAYING';score=0;level=1;baseSpeed=4.5;
 nitro=100;currentLap=1;distanceCovered=0;enemies=[];obstacles=[];particles=[];
 player.lane=1;player.x=190;
 document.getElementById('startScreen').style.display='none';
 document.getElementById('gameOverScreen').style.display='none';
 document.getElementById('victoryScreen').style.display='none';
 document.getElementById('pauseScreen').style.display='none';
}
function spawnEntities(){
 if(Math.random()<.025+level*.004){
  let lane=Math.floor(Math.random()*3),safe=true;
  for(let en of enemies)if(en.lane===lane&&en.y<0)safe=false;
  if(safe){
   let colors=['#00ffcc','#ffcc00','#ff00ff','#3388ff','#ff5500'];
   enemies.push({lane,x:lanes[lane],y:-100,width:40,height:75,
   speed:1.8+Math.random()*1.5+level*.4,color:colors[Math.floor(Math.random()*colors.length)]})
  }
 }
 if(level>=3&&Math.random()<.015){
  let lane=Math.floor(Math.random()*3),safe=true;
  for(let o of obstacles)if(o.lane===lane&&o.y<0)safe=false;
  if(safe)obstacles.push({lane,x:lanes[lane],y:-80,width:35,height:35})
 }
}
function collide(a,b){
 return a.x-a.width/2<b.x+b.width/2&&a.x+a.width/2>b.x-b.width/2&&
 a.y<b.y+b.height&&a.y+a.height>b.y;
}
function update(){
 if(gameState!=='PLAYING')return;
 if(accelerateHeld)baseSpeed=Math.min(maxSpeed,baseSpeed+.04);
 if(brakeHeld)baseSpeed=Math.max(2.5,baseSpeed-.06);
 if(isNitroActive){
  if(nitro>0){speed=baseSpeed*1.7;nitro-=.7;
   for(let i=0;i<3;i++)particles.push({x:player.x-12+Math.random()*24,y:player.y+75,
   vx:(Math.random()-.5)*1.5,vy:3+Math.random()*3,radius:3+Math.random()*4,
   color:Math.random()>.4?'#ff3300':'#ffaa00',alpha:1})}
  else{isNitroActive=false;speed=baseSpeed}
 }else{if(nitro<100)nitro+=.25;speed=baseSpeed}
 document.getElementById('nitroBar').style.width=nitro+'%';
 document.getElementById('nitroPct').innerText=Math.floor(nitro);
 player.x+=(lanes[player.lane]-player.x)*.25;
 distanceCovered+=speed;score+=Math.floor(speed/1.5);
 if(distanceCovered>=targetDistancePerLap*currentLap){
  if(currentLap<maxLaps)currentLap++;
  else{gameState='VICTORY';document.getElementById('victoryText').innerText=
  `Tổng điểm: ${score} - Bạn đã hoàn thành 3 vòng đua!`;
  document.getElementById('victoryScreen').style.display='flex'}
 }
 level=Math.floor(score/1200)+1;baseSpeed=Math.min(maxSpeed,4.5+(level-1)*.7);
 roadLinesOffset=(roadLinesOffset+speed)%35;spawnEntities();
 for(let i=enemies.length-1;i>=0;i--){
  let en=enemies[i];en.y+=speed-en.speed;en.x=lanes[en.lane];
  if(collide(player,en)){triggerGameOver();return}
  if(en.y>canvas.height+80)enemies.splice(i,1)
 }
 for(let i=obstacles.length-1;i>=0;i--){
  let o=obstacles[i];o.y+=speed;o.x=lanes[o.lane];
  if(collide(player,o)){triggerGameOver();return}
  if(o.y>canvas.height+50)obstacles.splice(i,1)
 }
 for(let i=particles.length-1;i>=0;i--){let p=particles[i];p.x+=p.vx;p.y+=p.vy;p.alpha-=.05;
  if(p.alpha<=0)particles.splice(i,1)}
 document.getElementById('scoreVal').innerText=score;
 document.getElementById('speedVal').innerText=Math.floor(speed*22);
 document.getElementById('lapVal').innerText=currentLap;
 document.getElementById('levelVal').innerText=level;
}
function triggerGameOver(){
 playSound('crash');gameState='GAMEOVER';
 if(score>highScore){highScore=score;document.getElementById('highScoreVal').innerText=highScore}
 document.getElementById('finalScoreText').innerText=`Điểm số đạt được: ${score} | Vòng: ${currentLap}/3`;
 document.getElementById('gameOverScreen').style.display='flex';
}
function drawCar(x,y,w,h,color,isPlayer=false){
 ctx.save();ctx.translate(x,y+h/2);ctx.fillStyle=color;ctx.fillRect(-w/2,-h/2,w,h);
 ctx.fillStyle='#0f141c';ctx.fillRect(-w/2+5,-h/4,w-10,16);ctx.fillRect(-w/2+5,h/4-8,w-10,10);
 ctx.fillStyle='#111';ctx.fillRect(-w/2-4,-h/3,5,16);ctx.fillRect(w/2-1,-h/3,5,16);
 ctx.fillRect(-w/2-4,h/4,5,16);ctx.fillRect(w/2-1,h/4,5,16);
 if(isPlayer){ctx.fillStyle='#ffff00';ctx.fillRect(-w/2+3,-h/2,6,3);ctx.fillRect(w/2-9,-h/2,6,3)}
 ctx.restore();
}
function draw(){
 ctx.clearRect(0,0,canvas.width,canvas.height);
 ctx.fillStyle='#1b4d3e';ctx.fillRect(0,0,25,canvas.height);ctx.fillRect(355,0,25,canvas.height);
 ctx.fillStyle='#161b22';ctx.fillRect(25,0,330,canvas.height);
 ctx.fillStyle='#f0f6fc';ctx.fillRect(25,0,5,canvas.height);ctx.fillRect(350,0,5,canvas.height);
 ctx.strokeStyle='#e3b341';ctx.lineWidth=3;ctx.setLineDash([18,18]);ctx.lineDashOffset=-roadLinesOffset;
 [130,250].forEach(x=>{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,canvas.height);ctx.stroke()});ctx.setLineDash([]);
 for(let p of particles){ctx.fillStyle=p.color;ctx.globalAlpha=p.alpha;ctx.beginPath();
  ctx.arc(p.x,p.y,p.radius,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1}
 for(let o of obstacles){ctx.fillStyle='#ff5555';ctx.fillRect(o.x-o.width/2,o.y,o.width,o.height)}
 enemies.forEach(e=>drawCar(e.x,e.y,e.width,e.height,e.color));
 drawCar(player.x,player.y,player.width,player.height,player.color,true);
}
window.addEventListener('keydown',e=>{
 initAudio();
 if(e.code==='ArrowLeft')moveLeft();if(e.code==='ArrowRight')moveRight();
 if(e.code==='ArrowUp'){e.preventDefault();accelerateHeld=true}
 if(e.code==='ArrowDown'){e.preventDefault();brakeHeld=true}
 if(e.code==='Space'){e.preventDefault();useNitro()}
});
window.addEventListener('keyup',e=>{
 if(e.code==='ArrowUp')accelerateHeld=false;if(e.code==='ArrowDown')brakeHeld=false;
 if(e.code==='Space')isNitroActive=false;
});
function loop(){update();draw();requestAnimationFrame(loop)}
document.getElementById('highScoreVal').innerText=highScore;
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=680, scrolling=False)

st.markdown("---")
st.markdown("### 📌 Hướng Dẫn Điều Khiển")
col1,col2=st.columns(2)
with col1:
    st.markdown("**💻 Máy tính:**")
    st.markdown("- ← / →: Chuyển làn\n- ↑ / ↓: Gas / Phanh\n- Space: Nitro")
with col2:
    st.markdown("**📱 Điện thoại:**")
    st.markdown("- Trái / Phải: Chuyển làn\n- Gas / Phanh / Nitro\n- Pause để tạm dừng")
