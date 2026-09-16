import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pixel Dash - 2D Retro Platformer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<style>
*{box-sizing:border-box;margin:0;padding:0;user-select:none;-webkit-user-select:none}
body{background:#0d0d15;font-family:monospace;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;color:white;overflow:hidden}
#game-wrapper{position:relative;width:100%;max-width:960px;box-shadow:0 0 20px rgba(0,255,200,.2);border-radius:8px;overflow:hidden;border:4px solid #1f293d;background:#000}
canvas{display:block;width:100%;height:auto;image-rendering:pixelated}
#mobile-controls{display:none;width:100%;max-width:960px;margin-top:10px;padding:0 10px;justify-content:space-between;touch-action:none}
.d-pad,.action-pad{display:flex;gap:12px}
.btn{background:#2a2f45;border:3px solid #4f5878;color:#fff;font-weight:bold;font-size:20px;border-radius:12px;padding:15px 25px;touch-action:none;box-shadow:0 5px 0 #181b29}
.btn:active{transform:translateY(4px);box-shadow:0 1px 0 #181b29}
.btn-jump{background:#008a55;border-color:#00ff99;padding:15px 35px}
@media(max-width:768px){#mobile-controls{display:flex}}
</style>
</head>
<body>
<div id="game-wrapper"><canvas id="gameCanvas" width="960" height="540"></canvas></div>
<div id="mobile-controls">
<div class="d-pad"><button class="btn" id="btn-left">◀</button><button class="btn" id="btn-right">▶</button></div>
<div class="action-pad"><button class="btn btn-jump" id="btn-jump">JUMP ⬆</button></div>
</div>

<script>
const C=document.getElementById("gameCanvas"),X=C.getContext("2d");
const W=960,H=540,G=.55,T=40;
let state="START",score=0,coins=0,lives=3,camera=0,shake=0;
const keys={left:false,right:false,jump:false};
let particles=[],tiles=[],coinItems=[],enemies=[],flag={x:0,y:0,w:40,h:160};
let checkpointX=100,checkpointY=400;

class AudioSys{
 constructor(){this.ctx=null}
 init(){if(!this.ctx)this.ctx=new(window.AudioContext||window.webkitAudioContext)()}
 tone(f,type,d,v=.1){if(!this.ctx)return;try{
  const o=this.ctx.createOscillator(),g=this.ctx.createGain();
  o.type=type;o.frequency.value=f;g.gain.setValueAtTime(v,this.ctx.currentTime);
  g.gain.exponentialRampToValueAtTime(.01,this.ctx.currentTime+d);
  o.connect(g);g.connect(this.ctx.destination);o.start();o.stop(this.ctx.currentTime+d)
 }catch(e){}}
 jump(){this.tone(260,"square",.12,.08);setTimeout(()=>this.tone(520,"square",.08,.06),60)}
 coin(){this.tone(988,"sine",.08,.1);setTimeout(()=>this.tone(1319,"sine",.12,.1),80)}
 stomp(){this.tone(180,"triangle",.1,.15)}
 hurt(){this.tone(110,"sawtooth",.25,.18)}
 win(){[262,330,392,523].forEach((n,i)=>setTimeout(()=>this.tone(n,"square",.18,.1),i*120))}
}
const audio=new AudioSys();

const MAP=[
"                                                                                                                        ",
"                                                                                                                        ",
"                                                                                                                        ",
"                                                                                 5 5 5                                  ",
"                                         5 5 5                                  111111                                  ",
"                                        23232                                  1      1                                 ",
"                                                                              1        1                                ",
"                   5 5 5                                                     1          1                               ",
"                  23232                      232                           1            1                               ",
"                                                                          1              1              7                 ",
"                                   4                   4                 1                1             1                 ",
"             232                 1111                 111               1                  1           111                ",
"                                1    1               1   1             1                    1         11111               ",
"          6           6        1      1     6       1     1     6     1                      1   6   1111111              ",
"11111111111111111111111111111111      111111111111111     1111111111111                      111111111111111111111111111111"
];

function collide(a,b){return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y}
function particle(x,y,c,vx,vy,life){particles.push({x,y,c,vx,vy,life})}

class Enemy{
 constructor(x,y){this.x=x;this.y=y;this.w=32;this.h=32;this.vx=-1.5;this.alive=true}
 update(){
  if(!this.alive)return;
  this.x+=this.vx;
  let wall=false;
  for(const t of tiles)if(collide(this,t)){wall=true;break}
  if(wall){this.x-=this.vx;this.vx*=-1}
 }
 draw(){
  if(!this.alive)return;
  const x=this.x-camera,y=this.y;
  X.fillStyle="#dc2626";X.fillRect(x+2,y+6,28,22);X.fillRect(x+6,y+2,20,26);
  X.fillStyle="#fff";X.fillRect(x+6,y+8,6,8);X.fillRect(x+20,y+8,6,8);
  X.fillStyle="#000";X.fillRect(x+8,y+10,4,4);X.fillRect(x+22,y+10,4,4);
  X.fillStyle="#991b1b";X.fillRect(x+2,y+26,8,6);X.fillRect(x+22,y+26,8,6);
 }
}

class Player{
 constructor(){this.w=32;this.h=44;this.speed=4.5;this.jump=-12.5;this.reset(100,400);this.grounded=false;this.face=1;this.anim=0;this.inv=0}
 reset(x,y){this.x=x;this.y=y;this.vx=0;this.vy=0}
 update(){
  if(keys.left){this.vx=-this.speed;this.face=-1}
  else if(keys.right){this.vx=this.speed;this.face=1}
  else{this.vx*=.7;if(Math.abs(this.vx)<.1)this.vx=0}
  if(keys.jump&&this.grounded){this.vy=this.jump;this.grounded=false;audio.jump();for(let i=0;i<6;i++)particle(this.x+16,this.y+44,"#fff",(Math.random()-.5)*3,-Math.random()*2,15)}
  this.vy+=G;if(this.inv>0)this.inv--;
  this.anim++;
  this.x+=this.vx;this.collideX();
  this.y+=this.vy;this.grounded=false;this.collideY();
  if(this.y>H+200)this.damage(true)
 }
 collideX(){
  for(const t of tiles)if(collide(this,t)){if(this.vx>0)this.x=t.x-this.w;else if(this.vx<0)this.x=t.x+t.w}
 }
 collideY(){
  for(const t of tiles)if(collide(this,t)){
   if(this.vy>0){this.y=t.y-this.h;this.vy=0;this.grounded=true}
   else if(this.vy<0){this.y=t.y+t.h;this.vy=0;if(t.type==="block"&&t.active){t.active=false;coins++;score+=100;audio.coin();particle(t.x+20,t.y,"#ffd700",0,-3,20)}}
  }
 }
 damage(kill=false){
  if(this.inv>0&&!kill)return;
  lives--;shake=15;audio.hurt();
  if(lives<=0)state="GAMEOVER";
  else{this.inv=60;this.reset(checkpointX,checkpointY)}
 }
 draw(){
  if(this.inv%6>3)return;
  X.save();X.translate(this.x-camera+16,this.y+22);X.scale(this.face,1);
  const moving=Math.abs(this.vx)>.5;
  X.fillStyle="#2563eb";X.fillRect(-12,-10,24,22);
  X.fillStyle="#ffdbac";X.fillRect(-10,-22,20,14);
  X.fillStyle="#ef4444";X.fillRect(-12,-26,26,6);X.fillRect(-6,-28,16,3);
  X.fillStyle="#000";X.fillRect(2,-18,3,4);
  X.fillStyle="#1e293b";
  if(!this.grounded){X.fillRect(-10,12,8,8);X.fillRect(2,8,8,8)}
  else if(moving){let o=(Math.floor(this.anim/6)%2)?4:-4;X.fillRect(-10+o,12,8,10);X.fillRect(2-o,12,8,10)}
  else{X.fillRect(-10,12,8,10);X.fillRect(2,12,8,10)}
  X.restore()
 }
}
const player=new Player();

function initMap(){
 tiles=[];coinItems=[];enemies=[];
 for(let r=0;r<MAP.length;r++)for(let c=0;c<MAP[r].length;c++){
  const ch=MAP[r][c],x=c*T,y=r*T;
  if(ch==="1")tiles.push({x,y,w:T,h:T,type:"ground"});
  else if(ch==="2")tiles.push({x,y,w:T,h:T,type:"brick"});
  else if(ch==="3")tiles.push({x,y,w:T,h:T,type:"block",active:true});
  else if(ch==="4")tiles.push({x,y,w:T,h:T,type:"pipe"});
  else if(ch==="5")coinItems.push({x:x+10,y:y+10,w:20,h:20,collected:false});
  else if(ch==="6")enemies.push(new Enemy(x,y));
  else if(ch==="7")flag={x,y,w:40,h:160};
 }
}
function resetGame(){
 score=0;coins=0;lives=3;camera=0;checkpointX=100;checkpointY=400;particles=[];
 initMap();player.reset(100,400);state="PLAYING";
}
function update(){
 if(state!=="PLAYING")return;
 player.update();
 for(const e of enemies){
  e.update();
  if(e.alive&&collide(player,e)){
   if(player.vy>0&&player.y+player.h-player.vy<=e.y+12){
    e.alive=false;player.vy=-8;score+=200;audio.stomp();
    for(let i=0;i<8;i++)particle(e.x+16,e.y+16,"#dc2626",(Math.random()-.5)*4,(Math.random()-.5)*4,20)
   }else player.damage()
  }
 }
 for(const c of coinItems)if(!c.collected&&collide(player,c)){
  c.collected=true;coins++;score+=50;audio.coin();particle(c.x+10,c.y+10,"#facc15",0,-2,15)
 }
 if(flag&&collide(player,flag)){state="WIN";audio.win()}
 camera+=(player.x-W/3-camera)*.1;if(camera<0)camera=0;
 if(shake>0)shake--;
 for(let i=particles.length-1;i>=0;i--){const p=particles[i];p.x+=p.vx;p.y+=p.vy;p.life--;if(p.life<=0)particles.splice(i,1)}
}
function background(){
 const g=X.createLinearGradient(0,0,0,H);g.addColorStop(0,"#0f172a");g.addColorStop(1,"#1e1b4b");X.fillStyle=g;X.fillRect(0,0,W,H);
 X.fillStyle="#1e293b";
 for(let i=-1;i<5;i++){let m=i*400-(camera*.2)%400;X.beginPath();X.moveTo(m,H);X.lineTo(m+200,H-180);X.lineTo(m+400,H);X.fill()}
 X.fillStyle="rgba(255,255,255,.15)";
 for(let i=-1;i<6;i++){let c=i*300-(camera*.4)%300;X.fillRect(c,80,120,30);X.fillRect(c+20,65,80,45)}
}
function drawMap(){
 for(const t of tiles){
  if(t.x+t.w<camera||t.x>camera+W)continue;
  const x=t.x-camera;
  if(t.type==="ground"){X.fillStyle="#15803d";X.fillRect(x,t.y,t.w,8);X.fillStyle="#854d0e";X.fillRect(x,t.y+8,t.w,t.h-8)}
  else if(t.type==="brick"){X.fillStyle="#b45309";X.fillRect(x,t.y,t.w,t.h);X.strokeStyle="#78350f";X.strokeRect(x,t.y,t.w,t.h)}
  else if(t.type==="block"){X.fillStyle=t.active?"#eab308":"#64748b";X.fillRect(x,t.y,t.w,t.h);if(t.active){X.fillStyle="#fff";X.font="bold 20px monospace";X.fillText("?",x+14,t.y+28)}}
  else{X.fillStyle="#16a34a";X.fillRect(x,t.y,t.w,t.h);X.strokeStyle="#14532d";X.strokeRect(x,t.y,t.w,t.h)}
 }
 for(const c of coinItems)if(!c.collected){X.fillStyle="#facc15";X.beginPath();X.arc(c.x-camera+10,c.y+10,8,0,Math.PI*2);X.fill()}
 const fx=flag.x-camera;X.fillStyle="#94a3b8";X.fillRect(fx+18,flag.y,4,flag.h);X.fillStyle="#ef4444";X.beginPath();X.moveTo(fx+22,flag.y);X.lineTo(fx+60,flag.y+20);X.lineTo(fx+22,flag.y+40);X.fill()
}
function hud(){
 X.fillStyle="rgba(0,0,0,.45)";X.fillRect(0,0,W,42);X.fillStyle="#fff";X.font="bold 18px monospace";
 X.fillText("SCORE: "+String(score).padStart(6,"0"),20,27);
 X.fillText("COINS: x"+coins,270,27);X.fillText("LIVES: x"+lives,480,27);X.fillText("WORLD: 1-1",760,27)
}
function overlay(){
 X.textAlign="center";
 if(state==="START"){X.fillStyle="rgba(15,23,42,.86)";X.fillRect(0,0,W,H);X.fillStyle="#38bdf8";X.font="bold 48px monospace";X.fillText("PIXEL DASH 2D",W/2,180);X.fillStyle="#fff";X.font="20px monospace";X.fillText("A/D hoặc ◀/▶ để di chuyển",W/2,270);X.fillText("SPACE / W / ↑ để nhảy",W/2,310);X.fillStyle="#4ade80";X.fillText("NHẤN SPACE HOẶC CHẠM ĐỂ BẮT ĐẦU",W/2,400)}
 if(state==="PAUSED"){X.fillStyle="rgba(0,0,0,.6)";X.fillRect(0,0,W,H);X.fillStyle="#fbbf24";X.font="bold 42px monospace";X.fillText("TẠM DỪNG",W/2,H/2)}
 if(state==="GAMEOVER"){X.fillStyle="rgba(23,23,23,.9)";X.fillRect(0,0,W,H);X.fillStyle="#ef4444";X.font="bold 52px monospace";X.fillText("GAME OVER",W/2,220);X.fillStyle="#fff";X.font="20px monospace";X.fillText("Điểm: "+score,W/2,290);X.fillStyle="#4ade80";X.fillText("Nhấn SPACE để chơi lại",W/2,370)}
 if(state==="WIN"){X.fillStyle="rgba(15,23,42,.9)";X.fillRect(0,0,W,H);X.fillStyle="#4ade80";X.font="bold 52px monospace";X.fillText("YOU WIN!",W/2,220);X.fillStyle="#fff";X.font="20px monospace";X.fillText("Tổng điểm: "+score,W/2,290);X.fillStyle="#38bdf8";X.fillText("Nhấn SPACE để chơi lại",W/2,370)}
 X.textAlign="left"
}
function render(){
 X.save();if(shake){X.translate((Math.random()-.5)*8,(Math.random()-.5)*8)}
 background();drawMap();enemies.forEach(e=>e.draw());if(state!=="START")player.draw();
 particles.forEach(p=>{X.fillStyle=p.c;X.fillRect(p.x-camera,p.y,4,4)});X.restore();hud();overlay()
}
function loop(){update();render();requestAnimationFrame(loop)}

function startOrReset(){audio.init();if(state==="START"||state==="GAMEOVER"||state==="WIN")resetGame()}
window.addEventListener("keydown",e=>{
 audio.init();
 if(["ArrowLeft","ArrowRight","ArrowUp","Space"].includes(e.code))e.preventDefault();
 if(e.code==="KeyA"||e.code==="ArrowLeft")keys.left=true;
 if(e.code==="KeyD"||e.code==="ArrowRight")keys.right=true;
 if(e.code==="Space"||e.code==="KeyW"||e.code==="ArrowUp"){keys.jump=true;startOrReset()}
 if(e.code==="KeyP")state=state==="PLAYING"?"PAUSED":state==="PAUSED"?"PLAYING":state;
});
window.addEventListener("keyup",e=>{
 if(e.code==="KeyA"||e.code==="ArrowLeft")keys.left=false;
 if(e.code==="KeyD"||e.code==="ArrowRight")keys.right=false;
 if(e.code==="Space"||e.code==="KeyW"||e.code==="ArrowUp")keys.jump=false;
});
function bind(id,k){
 const b=document.getElementById(id);
 ["touchstart","mousedown"].forEach(ev=>b.addEventListener(ev,e=>{e.preventDefault();audio.init();if(state==="START"||state==="GAMEOVER"||state==="WIN"){resetGame();return}keys[k]=true}));
 ["touchend","touchcancel","mouseup","mouseleave"].forEach(ev=>b.addEventListener(ev,e=>{e.preventDefault();keys[k]=false}))
}
bind("btn-left","left");bind("btn-right","right");bind("btn-jump","jump");
C.addEventListener("click",startOrReset);
initMap();requestAnimationFrame(loop);
</script>
</body>
</html>
"""

st.title("🎮 Pixel Dash - 2D Retro Platformer")
st.caption("Platformer retro nguyên bản — Python + Streamlit + HTML5 Canvas.")
components.html(GAME_HTML, height=660, scrolling=False)
