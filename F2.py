import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Cyber Arcade Racing 2D",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "high_score" not in st.session_state:
    st.session_state.high_score = 0

st.markdown("""
<style>
.stApp{background:#05050a;color:white}
h1{text-align:center;background:linear-gradient(90deg,#00ffcc,#ff007f);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:monospace;font-weight:900}
.instruction{text-align:center;color:#00ffcc;font-size:13px;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏎️ CYBER ARCADE RACING 2D</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='instruction'>⚡ NEON SYNTHWAVE • TỐI ƯU iPHONE • SẴN SÀNG ĐUA ⚡</div>",
    unsafe_allow_html=True,
)

game_html = f"""
<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<style>
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
html,body{{margin:0;background:#05050a;color:#fff;font-family:monospace;overflow:hidden;
touch-action:none;user-select:none;-webkit-user-select:none}}
body{{display:flex;flex-direction:column;align-items:center;padding-bottom:env(safe-area-inset-bottom)}}
#game{{position:relative;width:min(100vw - 12px,400px);height:min(calc(100vh - 185px),560px);
min-height:500px;background:#0b0b16;border:3px solid #00ffcc;border-radius:14px;overflow:hidden;
box-shadow:0 0 30px rgba(0,255,204,.4),inset 0 0 25px rgba(255,0,127,.2)}}
canvas{{width:100%;height:100%;display:block}}
.hud{{position:absolute;top:7px;left:7px;right:7px;display:grid;grid-template-columns:repeat(3,1fr);
gap:4px;background:rgba(5,5,15,.88);border:1px solid #00ffcc;border-radius:7px;padding:5px;
font-size:10px;font-weight:bold;text-align:center;z-index:3}}
.hud span{{color:#fff}}
.nitro{{position:absolute;left:8px;right:8px;bottom:8px;height:10px;border:1px solid #ff007f;
border-radius:6px;background:#08080f;overflow:hidden;z-index:3}}
.nitro i{{display:block;width:100%;height:100%;background:linear-gradient(90deg,#ff9900,#ff007f)}}
.screen{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
align-items:center;text-align:center;padding:25px;background:rgba(5,5,10,.95);z-index:10}}
.screen h2{{font-size:26px;color:#00ffcc;text-shadow:0 0 16px #00ffcc;margin:0 0 10px}}
.screen p{{font-size:13px;line-height:1.5;color:#c8c8e8;margin:5px 0 18px}}
.btn{{border:0;border-radius:28px;padding:14px 30px;background:linear-gradient(90deg,#00ffcc,#00bfff);
color:#05050a;font:bold 17px monospace;box-shadow:0 0 18px rgba(0,255,204,.7);min-height:52px}}
.controls{{width:min(100vw - 12px,400px);display:grid;grid-template-columns:repeat(3,1fr);
gap:7px;margin-top:8px;padding-bottom:5px}}
.ctrl{{height:50px;border:2px solid #00ffcc;border-radius:9px;background:#111122;color:#00ffcc;
display:flex;align-items:center;justify-content:center;font:bold 13px monospace;touch-action:none}}
.ctrl:active,.ctrl.on{{background:#00ffcc;color:#05050a}}
@media(max-height:700px) and (orientation:portrait){{
#game{{height:calc(100vh - 165px);min-height:430px}}
.ctrl{{height:44px}}
}}
</style>
</head>
<body>
<div id="game">
<canvas id="c" width="400" height="560"></canvas>

<div class="hud">
<div>ĐIỂM<br><span id="score">0</span></div>
<div>TỐC ĐỘ<br><span id="spd">0</span> KM/H</div>
<div>VÒNG<br><span id="lap">1</span>/3</div>
<div>CẤP<br><span id="lvl">1</span></div>
<div>KỶ LỤC<br><span id="hi">{st.session_state.high_score}</span></div>
<div>NITRO<br><span id="np">100</span>%</div>
</div>

<div class="nitro"><i id="nb"></i></div>

<div id="start" class="screen">
<h2>🏁 CYBER RACING 🏁</h2>
<p>Phong cách Cyberpunk Neon.<br>Né xe địch • Bứt phá Nitro • Hoàn thành 3 vòng!</p>
<button class="btn" onclick="startGame()">▶ KHỞI ĐỘNG XE</button>
</div>

<div id="pause" class="screen" style="display:none">
<h2>TẠM DỪNG</h2><button class="btn" onclick="pause()">TIẾP TỤC ĐUA</button>
</div>

<div id="over" class="screen" style="display:none">
<h2 style="color:#ff007f">💥 GAME OVER</h2><p id="final"></p>
<button class="btn" onclick="startGame()">🔄 THỬ LẠI</button>
</div>

<div id="win" class="screen" style="display:none">
<h2 style="color:#ffff00">🏆 CHIẾN THẮNG!</h2><p id="victory"></p>
<button class="btn" onclick="startGame()">🏎️ ĐUA LẠI</button>
</div>
</div>

<div class="controls">
<div class="ctrl" id="left">⬅️ TRÁI</div>
<div class="ctrl" id="nit">⚡ NITRO</div>
<div class="ctrl" id="right">PHẢI ➡️</div>
<div class="ctrl" id="gas">⛽ GAS</div>
<div class="ctrl" id="pauseBtn">⏸️ PAUSE</div>
<div class="ctrl" id="brake">🛑 PHANH</div>
</div>

<script>
const c=document.getElementById("c"),x=c.getContext("2d");
let state="START",score=0,hi={st.session_state.high_score},level=1;
let base=5,speed=5,nitro=100,boost=false,lap=1,dist=0,shake=0;
const lanes=[85,200,315];
let car={{lane:1,x:200,y:440,w:44,h:80,color:"#00ffcc"}};
let enemies=[],obs=[],parts=[],road=0;
let gas=false,brakeHeld=false,last=performance.now();

function audio(t){{try{{let a=new(window.AudioContext||window.webkitAudioContext)(),o=a.createOscillator(),g=a.createGain();
o.connect(g);g.connect(a.destination);let n=a.currentTime;
o.frequency.value=t==="crash"?70:t==="nitro"?220:650;g.gain.setValueAtTime(.08,n);
g.gain.exponentialRampToValueAtTime(.001,n+.12);o.start();o.stop(n+.12)}}catch(e){{}}}}

function startGame(){{
audio("click");state="PLAYING";score=0;level=1;base=5;speed=5;nitro=100;boost=false;
lap=1;dist=0;enemies=[];obs=[];parts=[];car.lane=1;car.x=200;
["start","over","win","pause"].forEach(id=>document.getElementById(id).style.display="none");
}}
function pause(){{
if(state==="PLAYING"){{state="PAUSED";document.getElementById("pause").style.display="flex"}}
else if(state==="PAUSED"){{state="PLAYING";document.getElementById("pause").style.display="none"}}
}}
function left(){{if(state==="PLAYING"&&car.lane>0){{car.lane--;audio("click")}}}}
function right(){{if(state==="PLAYING"&&car.lane<2){{car.lane++;audio("click")}}}}
function nitroOn(){{if(state==="PLAYING"&&nitro>5){{boost=true;audio("nitro");shake=8}}}}
function nitroOff(){{boost=false}}
function spawn(){{
if(Math.random()<.025+level*.004){{
 let l=Math.floor(Math.random()*3);
 if(!enemies.some(e=>e.lane===l&&e.y<80))
 enemies.push({{lane:l,x:lanes[l],y:-100,w:44,h:80,
 speed:2+Math.random()*2+level*.25,color:["#ff007f","#00bfff","#ffff00","#bf00ff","#ff5500"][Math.floor(Math.random()*5)]}});
}}
if(level>=3&&Math.random()<.012){{
 let l=Math.floor(Math.random()*3);
 if(!obs.some(o=>o.lane===l&&o.y<80))obs.push({{lane:l,x:lanes[l],y:-60,w:38,h:38}});
}}
}}
function hit(a,b){{return a.x-a.w/2<b.x+b.w/2&&a.x+a.w/2>b.x-b.w/2&&a.y<b.y+b.h&&a.y+a.h>b.y}}
function gameOver(){{
audio("crash");state="GAMEOVER";shake=18;
if(score>hi)hi=score;
document.getElementById("hi").textContent=hi;
document.getElementById("final").textContent="Điểm: "+score+" • Vòng: "+lap+"/3";
document.getElementById("over").style.display="flex";
}}
function update(dt){{
if(state!=="PLAYING")return;
if(gas)base=Math.min(12,base+.03);if(brakeHeld)base=Math.max(3,base-.05);
if(boost&&nitro>0){{speed=base*1.8;nitro-=35*dt;
for(let i=0;i<3;i++)parts.push({{x:car.x+(Math.random()-.5)*20,y:car.y+car.h,
vy:3+Math.random()*3,r:3+Math.random()*3,a:1}})}}else{{boost=false;speed=base;nitro=Math.min(100,nitro+8*dt)}}
car.x+=(lanes[car.lane]-car.x)*Math.min(1,dt*12);
dist+=speed*60*dt;score+=Math.floor(speed*dt*8);
if(dist>=2500*lap){{if(lap<3){{lap++}}else{{state="WIN";document.getElementById("victory").textContent="Tổng điểm: "+score;
document.getElementById("win").style.display="flex"}}}}
level=Math.floor(score/1200)+1;base=Math.min(12,5+(level-1)*.65);road=(road+speed*60*dt)%40;
spawn();
for(let i=enemies.length-1;i>=0;i--){{let e=enemies[i];e.y+=(speed-e.speed)*60*dt;e.x=lanes[e.lane];
if(hit(car,e)){{gameOver();return}}if(e.y>600)enemies.splice(i,1)}}
for(let i=obs.length-1;i>=0;i--){{let o=obs[i];o.y+=speed*60*dt;o.x=lanes[o.lane];
if(hit(car,o)){{gameOver();return}}if(o.y>600)obs.splice(i,1)}}
for(let i=parts.length-1;i>=0;i--){{let p=parts[i];p.y+=p.vy;p.a-=dt*2.5;if(p.a<=0)parts.splice(i,1)}}
document.getElementById("score").textContent=score;document.getElementById("spd").textContent=Math.floor(speed*22);
document.getElementById("lap").textContent=lap;document.getElementById("lvl").textContent=level;
document.getElementById("np").textContent=Math.floor(nitro);document.getElementById("nb").style.width=nitro+"%";
}}
function carDraw(a){{
x.save();x.translate(a.x,a.y+a.h/2);x.shadowBlur=18;x.shadowColor=a.color;
let g=x.createLinearGradient(-a.w/2,0,a.w/2,0);g.addColorStop(0,"#050505");g.addColorStop(.35,a.color);g.addColorStop(.65,a.color);g.addColorStop(1,"#050505");
x.fillStyle=g;x.fillRect(-a.w/2,-a.h/2,a.w,a.h);x.strokeStyle=a.color;x.lineWidth=2;x.strokeRect(-a.w/2+2,-a.h/2+2,a.w-4,a.h-4);
x.shadowBlur=0;x.fillStyle="#050510";x.fillRect(-a.w/2+6,-a.h/4,a.w-12,18);x.fillRect(-a.w/2+6,a.h/4-10,a.w-12,12);
x.fillStyle="#000";for(let yy of [-a.h/3,a.h/4]){{x.fillRect(-a.w/2-5,yy,6,18);x.fillRect(a.w/2-1,yy,6,18)}}
x.fillStyle=a===car?"#00ffff":"#ff0055";x.shadowBlur=10;x.shadowColor=x.fillStyle;x.fillRect(-a.w/2+4,-a.h/2,8,4);x.fillRect(a.w/2-12,-a.h/2,8,4);
x.restore();
}}
function draw(){{
x.save();if(shake>.5){{x.translate((Math.random()-.5)*shake,(Math.random()-.5)*shake);shake*=.86}}
x.clearRect(0,0,400,560);x.fillStyle="#090914";x.fillRect(0,0,400,560);
x.fillStyle="#0a1020";x.fillRect(30,0,340,560);x.fillStyle="#00ffcc";x.shadowBlur=10;x.shadowColor="#00ffcc";x.fillRect(30,0,4,560);x.fillRect(366,0,4,560);
x.strokeStyle="#ff007f";x.lineWidth=3;x.shadowBlur=8;x.shadowColor="#ff007f";x.setLineDash([20,20]);x.lineDashOffset=-road;
[150,250].forEach(q=>{{x.beginPath();x.moveTo(q,0);x.lineTo(q,560);x.stroke()}});x.setLineDash([]);x.shadowBlur=0;
for(let i=0;i<10;i++){{let yy=(i*65+road)%650-80;x.fillStyle="#ff007f";x.fillRect(12,yy,5,18);x.fillRect(383,yy,5,18)}}
obs.forEach(o=>{{x.fillStyle="#330033";x.strokeStyle="#ff0055";x.shadowBlur=12;x.shadowColor="#ff0055";x.fillRect(o.x-o.w/2,o.y,o.w,o.h);x.strokeRect(o.x-o.w/2,o.y,o.w,o.h);x.shadowBlur=0}});
enemies.forEach(e=>carDraw(e));parts.forEach(p=>{{x.globalAlpha=p.a;x.fillStyle="#ff9900";x.beginPath();x.arc(p.x,p.y,p.r,0,7);x.fill();x.globalAlpha=1}});
carDraw(car);x.restore();
}}
function loop(now){{let dt=Math.min(.033,(now-last)/1000);last=now;update(dt);draw();requestAnimationFrame(loop)}}requestAnimationFrame(loop);

function bind(id,down,up=()=>{{}}){{let el=document.getElementById(id);
el.addEventListener("pointerdown",e=>{{e.preventDefault();el.classList.add("on");down()}});
["pointerup","pointercancel","pointerleave"].forEach(t=>el.addEventListener(t,e=>{{e.preventDefault();el.classList.remove("on");up()}}));}}
bind("left",left);bind("right",right);bind("nit",nitroOn,nitroOff);bind("gas",()=>gas=true,()=>gas=false);
bind("brake",()=>brakeHeld=true,()=>brakeHeld=false);bind("pause",pause);
document.getElementById("pauseBtn").addEventListener("pointerdown",e=>{{e.preventDefault();pause()}});
window.addEventListener("keydown",e=>{{
if(e.code==="ArrowLeft")left();if(e.code==="ArrowRight")right();if(e.code==="ArrowUp")gas=true;
if(e.code==="ArrowDown")brakeHeld=true;if(e.code==="Space")nitroOn();if(e.code==="KeyP")pause();
}});
window.addEventListener("keyup",e=>{{if(e.code==="ArrowUp")gas=false;if(e.code==="ArrowDown")brakeHeld=false;if(e.code==="Space")nitroOff()}});
window.addEventListener("blur",()=>{{gas=false;brakeHeld=false;boost=false}});
</script>
</body>
</html>
"""

components.html(game_html, height=790, scrolling=False)

st.markdown(
    "📱 **iPhone:** dùng các nút cảm ứng. Giữ **GAS / PHANH / NITRO** để điều khiển. "
    "💻 **PC:** dùng ← → ↑ ↓ và Space."
)
