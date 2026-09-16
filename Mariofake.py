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
body{background:#070b14;font-family:monospace;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;color:#fff;overflow:hidden}
#game-wrapper{position:relative;width:100%;max-width:960px;border:4px solid #263248;border-radius:10px;overflow:hidden;background:#000;box-shadow:0 0 30px rgba(0,220,255,.18)}
canvas{display:block;width:100%;height:auto;image-rendering:pixelated}
#mobile-controls{display:flex;width:100%;max-width:960px;margin-top:10px;padding:0 8px;justify-content:space-between;touch-action:none}
.pad{display:flex;gap:10px}.btn{border:3px solid #56627f;background:#252d43;color:#fff;border-radius:12px;font:bold 20px monospace;padding:13px 24px;box-shadow:0 5px 0 #101522;touch-action:none}
.btn:active{transform:translateY(4px);box-shadow:0 1px 0 #101522}.jump{background:#087f55;border-color:#00e99a;padding:13px 30px}
@media(min-width:769px){#mobile-controls{display:none}}
</style>
</head>
<body>
<div id="game-wrapper"><canvas id="game" width="960" height="540"></canvas></div>
<div id="mobile-controls"><div class="pad"><button class="btn" id="l">◀</button><button class="btn" id="r">▶</button></div><div class="pad"><button class="btn jump" id="j">JUMP ⬆</button></div></div>

<script>
const C=document.getElementById("game"),ctx=C.getContext("2d"),W=960,H=540,T=40;
const GR=.58,MAX_LEVELS=3;
let state="START",level=1,score=0,coins=0,lives=3,camera=0,shake=0;
let power=0,powerTimer=0,checkpoint={x:80,y:400},flag={x:0,y:0};
let keys={left:false,right:false,jump:false},tiles=[],items=[],enemies=[],particles=[],stars=[];
for(let i=0;i<90;i++)stars.push({x:Math.random()*5000,y:Math.random()*220,s:Math.random()*2+1});

class AudioSys{
 constructor(){this.ctx=null;this.music=null;this.step=0}
 init(){if(!this.ctx)this.ctx=new(window.AudioContext||window.webkitAudioContext)();if(this.ctx.state==="suspended")this.ctx.resume()}
 tone(f,type,d,v=.07){if(!this.ctx)return;let o=this.ctx.createOscillator(),g=this.ctx.createGain();o.type=type;o.frequency.value=f;g.gain.setValueAtTime(v,this.ctx.currentTime);g.gain.exponentialRampToValueAtTime(.005,this.ctx.currentTime+d);o.connect(g);g.connect(this.ctx.destination);o.start();o.stop(this.ctx.currentTime+d)}
 jump(){this.tone(260,"square",.11,.07);setTimeout(()=>this.tone(520,"square",.08,.05),55)}
 coin(){this.tone(880,"sine",.07,.09);setTimeout(()=>this.tone(1320,"sine",.11,.08),70)}
 stomp(){this.tone(140,"triangle",.12,.12)}
 hurt(){this.tone(90,"sawtooth",.25,.16)}
 power(){this.tone(440,"square",.1,.09);setTimeout(()=>this.tone(660,"square",.14,.09),90)}
 win(){[262,330,392,523,659].forEach((n,i)=>setTimeout(()=>this.tone(n,"square",.16,.08),i*100))}
 startMusic(){if(this.music||!this.ctx)return;this.music=setInterval(()=>{if(state==="PLAYING"){let n=[196,247,294,330,294,247][this.step++%6];this.tone(n,"square",.055,.018)}},190)}
}
const audio=new AudioSys();

const MAPS=[
[
"                                                                                ",
"                              5      5       5                                  ",
"                         B   BBB    B B     BBB                    M             ",
"                 5                          5                                  ",
"          BBB          4              4             E             F             ",
"                                                        BBB       1111           ",
"             E                    M                                      111      ",
"11111111111111111     111111111111     1111111111111111             111111111111",
""
],
[
"                                                                                ",
"       5         5             B B B                         5                  ",
"      BBB       BBB              M                         BBB                  ",
"                         E                    4                                ",
"               4                              111       E                      F ",
"       M                    BBB                            BBB                   ",
"                  E                 5       5                         M         ",
"1111111111111      1111111111111       1111111111111111       111111111111111111",
""
],
[
"                                                                                ",
"        5       B B B       5          B B B          5                         ",
"   E        M             E       M                 E       F                    ",
"       4                         4                         111                  ",
"             BBB      5                 BBB                   111                ",
"       M                    E                   M                 111             ",
"  E                 5                    E                         111           ",
"11111111111111     111111111111     1111111111111     11111111111111111111111111",
""
]
];

function makeLevel(n,infinite=false){
 tiles=[];items=[];enemies=[];
 const rows=MAPS[(n-1)%MAPS.length];
 const repeat=infinite?5:1;
 for(let rep=0;rep<repeat;rep++)for(let r=0;r<rows.length;r++){
  let row=rows[r];
  for(let c=0;c<row.length;c++){
   const ch=row[c],x=(rep*row.length+c)*T,y=r*T;
   if(ch==="1")tiles.push({x,y,w:T,h:T,type:"ground"});
   else if(ch==="B")tiles.push({x,y,w:T,h:T,type:"brick"});
   else if(ch==="4")tiles.push({x,y,w:T,h:T,type:"pipe"});
   else if(ch==="5")items.push({x:x+10,y:y+8,w:20,h:24,type:"coin",collected:false,phase:Math.random()*6});
   else if(ch==="M")items.push({x:x+5,y:y+5,w:30,h:30,type:"mushroom",collected:false});
   else if(ch==="E")enemies.push(new Enemy(x,y+8,"walker"));
   else if(ch==="F")flag={x:x,y:y,w:44,h:200};
  }
 }
 // Add flying enemies on later levels.
 if(n>=2) for(let i=0;i<5;i++) enemies.push(new Enemy(700+i*430,180+(i%2)*55,"flyer"));
 checkpoint={x:80,y:360}; camera=0; player.reset(checkpoint.x,checkpoint.y);
}
function hit(a,b){return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y}
function burst(x,y,c,n=8){for(let i=0;i<n;i++)particles.push({x,y,c,vx:(Math.random()-.5)*5,vy:(Math.random()-.5)*5-1,life:20+Math.random()*15})}

class Enemy{
 constructor(x,y,type){this.x=x;this.y=y;this.w=32;this.h=32;this.type=type;this.vx=type==="flyer"?1.4:-1.4;this.baseY=y;this.t=0;this.alive=true}
 update(){if(!this.alive)return;this.t++;this.x+=this.vx;
  if(this.type==="flyer")this.y=this.baseY+Math.sin(this.t*.05)*30;
  else{for(const t of tiles)if(hit(this,t)){this.x-=this.vx;this.vx*=-1;break}}
 }
 draw(){if(!this.alive)return;let x=this.x-camera,y=this.y;
  ctx.fillStyle=this.type==="flyer"?"#7c3aed":"#dc2626";
  ctx.fillRect(x+2,y+7,28,21);ctx.fillRect(x+7,y+2,18,28);
  ctx.fillStyle="#fff";ctx.fillRect(x+6,y+8,6,7);ctx.fillRect(x+20,y+8,6,7);
  ctx.fillStyle="#111";ctx.fillRect(x+8,y+10,3,3);ctx.fillRect(x+22,y+10,3,3);
  ctx.fillStyle="#333";ctx.fillRect(x+2,y+27,8,5);ctx.fillRect(x+22,y+27,8,5);
 }
}

class Player{
 constructor(){this.w=32;this.h=44;this.speed=4.5;this.jump=-12.4;this.reset(80,360);this.vx=0;this.vy=0;this.grounded=false;this.face=1;this.anim=0;this.inv=0}
 reset(x,y){this.x=x;this.y=y;this.vx=0;this.vy=0}
 update(){
  if(keys.left){this.vx=-this.speed;this.face=-1}else if(keys.right){this.vx=this.speed;this.face=1}else this.vx*=.72;
  if(keys.jump&&this.grounded){this.vy=this.jump;this.grounded=false;audio.jump();burst(this.x+16,this.y+44,"#dbeafe",6)}
  this.vy+=GR;if(this.inv>0)this.inv--;this.anim++;
  this.x+=this.vx;this.collideX();this.y+=this.vy;this.grounded=false;this.collideY();
  if(this.y>H+180)damage(true)
 }
 collideX(){for(const t of tiles)if(hit(this,t)){if(this.vx>0)this.x=t.x-this.w;else if(this.vx<0)this.x=t.x+t.w}}
 collideY(){for(const t of tiles)if(hit(this,t)){
  if(this.vy>0){this.y=t.y-this.h;this.vy=0;this.grounded=true}
  else if(this.vy<0){this.y=t.y+t.h;this.vy=0;
   if(t.type==="brick"&&Math.random()<.18){score+=25;burst(t.x+20,t.y,"#f59e0b",4)}
  }
 }}
 draw(){if(this.inv%6>3)return;ctx.save();ctx.translate(this.x-camera+16,this.y+22);ctx.scale(this.face,1);
  const run=Math.abs(this.vx)>.5,o=Math.floor(this.anim/5)%2?4:-4;
  ctx.fillStyle=power?"#f97316":"#2563eb";ctx.fillRect(-12,-10,24,22);
  ctx.fillStyle="#ffdbac";ctx.fillRect(-10,-22,20,14);
  ctx.fillStyle="#ef4444";ctx.fillRect(-12,-27,26,7);ctx.fillRect(-5,-30,15,4);
  ctx.fillStyle="#111";ctx.fillRect(3,-18,3,4);
  ctx.fillStyle="#172033";
  if(!this.grounded){ctx.fillRect(-10,12,8,9);ctx.fillRect(2,9,8,8)}
  else if(run){ctx.fillRect(-10+o,12,8,10);ctx.fillRect(2-o,12,8,10)}
  else{ctx.fillRect(-10,12,8,10);ctx.fillRect(2,12,8,10)}
  ctx.restore()
 }
}
const player=new Player();

function damage(kill=false){
 if(player.inv>0&&!kill)return;
 lives--;shake=18;audio.hurt();power=0;
 if(lives<=0)state="GAMEOVER";else{player.inv=70;player.reset(checkpoint.x,checkpoint.y)}
}
function nextLevel(){
 if(level<MAX_LEVELS){level++;makeLevel(level,false);state="PLAYING";audio.win()}
 else{state="WIN";audio.win()}
}
function update(){
 if(state!=="PLAYING")return;
 player.update();
 for(const e of enemies){e.update();if(e.alive&&hit(player,e)){
  if(player.vy>0&&player.y+player.h-player.vy<=e.y+12){e.alive=false;player.vy=-8;score+=200;audio.stomp();burst(e.x+16,e.y+16,"#ef4444",10)}
  else damage()
 }}
 for(const it of items)if(!it.collected&&hit(player,it)){
  it.collected=true;
  if(it.type==="coin"){coins++;score+=50;audio.coin();burst(it.x+10,it.y+10,"#facc15",8)}
  if(it.type==="mushroom"){power=1;powerTimer=900;score+=500;audio.power();burst(it.x+15,it.y+15,"#fb923c",12)}
 }
 if(powerTimer>0&&--powerTimer===0)power=0;
 if(player.x>checkpoint.x+650){checkpoint={x:player.x,y:360}}
 if(hit(player,flag))nextLevel();
 const target=player.x-W/3;camera+=(target-camera)*.1;if(camera<0)camera=0;
 if(shake>0)shake--;
 for(let i=particles.length-1;i>=0;i--){let p=particles[i];p.x+=p.vx;p.y+=p.vy;p.vy+=.12;p.life--;if(p.life<=0)particles.splice(i,1)}
}

function bg(){
 let g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,"#111827");g.addColorStop(1,"#312e81");ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 ctx.fillStyle="rgba(255,255,255,.7)";stars.forEach(s=>{let x=s.x-camera*.15;if(x>-5&&x<W+5)ctx.fillRect(x,s.y,s.s,s.s)});
 for(let layer=0;layer<3;layer++){ctx.fillStyle=["#172554","#1e3a5f","#234e52"][layer];let sp=.15+layer*.12;
  for(let i=-1;i<7;i++){let x=i*260-(camera*sp)%260;ctx.beginPath();ctx.moveTo(x,H);ctx.lineTo(x+130,H-100-layer*25);ctx.lineTo(x+260,H);ctx.fill()}
 }
 ctx.fillStyle="rgba(255,255,255,.13)";for(let i=-1;i<6;i++){let x=i*330-camera*.35%330;ctx.fillRect(x,75,120,25);ctx.fillRect(x+25,60,70,40)}
}
function mapDraw(){
 for(const t of tiles){if(t.x+t.w<camera||t.x>camera+W)continue;let x=t.x-camera;
  if(t.type==="ground"){ctx.fillStyle="#22c55e";ctx.fillRect(x,t.y,t.w,8);ctx.fillStyle="#854d0e";ctx.fillRect(x,t.y+8,t.w,t.h-8)}
  if(t.type==="brick"){ctx.fillStyle="#b45309";ctx.fillRect(x,t.y,t.w,t.h);ctx.strokeStyle="#78350f";ctx.strokeRect(x,t.y,t.w,t.h)}
  if(t.type==="pipe"){ctx.fillStyle="#16a34a";ctx.fillRect(x,t.y,t.w,t.h);ctx.fillStyle="#22c55e";ctx.fillRect(x-4,t.y,t.w+8,9)}
 }
 for(const it of items)if(!it.collected){
  let x=it.x-camera;
  if(it.type==="coin"){let bob=Math.sin(Date.now()*.008+it.phase)*3;ctx.fillStyle="#facc15";ctx.beginPath();ctx.arc(x+10,it.y+12+bob,9,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fff7b2";ctx.fillRect(x+8,it.y+6+bob,3,10)}
  else{ctx.fillStyle="#ef4444";ctx.fillRect(x+3,it.y+8,24,17);ctx.fillStyle="#fff";ctx.fillRect(x+7,it.y+4,8,8);ctx.fillStyle="#facc15";ctx.fillRect(x+15,it.y+4,8,8)}
 }
 let fx=flag.x-camera;ctx.fillStyle="#cbd5e1";ctx.fillRect(fx+18,flag.y,5,flag.h);ctx.fillStyle="#f43f5e";ctx.beginPath();ctx.moveTo(fx+23,flag.y);ctx.lineTo(fx+63,flag.y+20);ctx.lineTo(fx+23,flag.y+40);ctx.fill()
}
function hud(){
 ctx.fillStyle="rgba(0,0,0,.48)";ctx.fillRect(0,0,W,46);ctx.fillStyle="#fff";ctx.font="bold 17px monospace";
 ctx.fillText("SCORE "+String(score).padStart(6,"0"),18,29);ctx.fillText("COINS "+coins,245,29);ctx.fillText("LIVES "+lives,390,29);ctx.fillText("WORLD "+level+"-"+(level<4?level:"∞"),540,29);
 ctx.fillText(power?"POWER!":"NORMAL",750,29)
}
function overlay(){
 ctx.textAlign="center";
 if(state==="START"){ctx.fillStyle="rgba(5,10,25,.86)";ctx.fillRect(0,0,W,H);ctx.fillStyle="#38bdf8";ctx.font="bold 50px monospace";ctx.fillText("PIXEL DASH",W/2,175);ctx.fillStyle="#fff";ctx.font="20px monospace";ctx.fillText("Platformer Retro • PC + Mobile",W/2,225);ctx.fillText("A/D hoặc ◀ ▶  •  SPACE/W/↑ hoặc JUMP",W/2,275);ctx.fillStyle="#4ade80";ctx.fillText("NHẤN SPACE / CHẠM MÀN HÌNH ĐỂ BẮT ĐẦU",W/2,370);ctx.fillStyle="#facc15";ctx.fillText("Thu thập 🍄 để tăng sức mạnh!",W/2,415)}
 if(state==="PAUSED"){ctx.fillStyle="rgba(0,0,0,.65)";ctx.fillRect(0,0,W,H);ctx.fillStyle="#facc15";ctx.font="bold 44px monospace";ctx.fillText("PAUSED",W/2,270)}
 if(state==="GAMEOVER"){ctx.fillStyle="rgba(0,0,0,.88)";ctx.fillRect(0,0,W,H);ctx.fillStyle="#ef4444";ctx.font="bold 52px monospace";ctx.fillText("GAME OVER",W/2,220);ctx.fillStyle="#fff";ctx.font="20px monospace";ctx.fillText("SCORE: "+score,W/2,275);ctx.fillStyle="#4ade80";ctx.fillText("SPACE để chơi lại",W/2,350)}
 if(state==="WIN"){ctx.fillStyle="rgba(5,20,20,.9)";ctx.fillRect(0,0,W,H);ctx.fillStyle="#4ade80";ctx.font="bold 52px monospace";ctx.fillText("YOU WIN!",W/2,220);ctx.fillStyle="#fff";ctx.font="20px monospace";ctx.fillText("Bạn đã hoàn thành "+MAX_LEVELS+" màn!",W/2,275);ctx.fillText("SCORE: "+score+"  COINS: "+coins,W/2,310);ctx.fillStyle="#38bdf8";ctx.fillText("SPACE để chơi lại",W/2,365)}
 ctx.textAlign="left"
}
function render(){ctx.save();if(shake)ctx.translate((Math.random()-.5)*8,(Math.random()-.5)*8);bg();mapDraw();enemies.forEach(e=>e.draw());if(state!=="START")player.draw();particles.forEach(p=>{ctx.fillStyle=p.c;ctx.fillRect(p.x-camera,p.y,4,4)});ctx.restore();hud();overlay()}
function loop(){update();render();requestAnimationFrame(loop)}

function reset(){score=0;coins=0;lives=3;level=1;power=0;powerTimer=0;makeLevel(1,false);state="PLAYING";audio.init();audio.startMusic()}
function start(){audio.init();audio.startMusic();if(state==="START"||state==="GAMEOVER"||state==="WIN")reset()}
window.addEventListener("keydown",e=>{
 audio.init();if(["ArrowLeft","ArrowRight","ArrowUp","Space"].includes(e.code))e.preventDefault();
 if(e.code==="KeyA"||e.code==="ArrowLeft")keys.left=true;
 if(e.code==="KeyD"||e.code==="ArrowRight")keys.right=true;
 if(e.code==="Space"||e.code==="KeyW"||e.code==="ArrowUp"){keys.jump=true;start()}
 if(e.code==="KeyP")state=state==="PLAYING"?"PAUSED":state==="PAUSED"?"PLAYING":state;
});
window.addEventListener("keyup",e=>{
 if(e.code==="KeyA"||e.code==="ArrowLeft")keys.left=false;
 if(e.code==="KeyD"||e.code==="ArrowRight")keys.right=false;
 if(e.code==="Space"||e.code==="KeyW"||e.code==="ArrowUp")keys.jump=false;
});
function bind(id,k){let b=document.getElementById(id);["touchstart","mousedown"].forEach(ev=>b.addEventListener(ev,e=>{e.preventDefault();audio.init();if(state==="START"||state==="GAMEOVER"||state==="WIN"){reset();return}keys[k]=true}));["touchend","touchcancel","mouseup","mouseleave"].forEach(ev=>b.addEventListener(ev,e=>{e.preventDefault();keys[k]=false}))}
bind("l","left");bind("r","right");bind("j","jump");
C.addEventListener("click",start);
makeLevel(1,false);requestAnimationFrame(loop);
</script>
</body>
</html>
"""

st.title("🎮 Pixel Dash - 2D Retro Platformer")
st.caption("Platformer retro nguyên bản — Python + Streamlit + HTML5 Canvas.")
components.html(GAME_HTML, height=690, scrolling=False)

st.caption("Platformer retro nguyên bản — Python + Streamlit + HTML5 Canvas.")
components.html(GAME_HTML, height=660, scrolling=False)
