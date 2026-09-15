import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Arcade Fighter 2D", layout="wide",
                   initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "menu"
if "p1_char" not in st.session_state:
    st.session_state.p1_char = 0
if "difficulty" not in st.session_state:
    st.session_state.difficulty = 1
if "arena" not in st.session_state:
    st.session_state.arena = 0

CHARACTERS = [
    {"name": "BRAWLER", "desc": "Cân bằng", "color": "#ff3333"},
    {"name": "ASSASSIN", "desc": "Nhanh, combo mạnh", "color": "#33ff33"},
    {"name": "TITAN", "desc": "Trâu, sát thương lớn", "color": "#ffaa00"},
    {"name": "ZONER", "desc": "Đánh xa, hồi năng lượng nhanh", "color": "#33ccff"}
]
ARENAS = ["NIGHT CITY", "DOJO", "CYBER STREET", "NEON ARENA"]
DIFFICULTIES = ["EASY", "NORMAL", "HARD", "EXPERT"]

def get_game_html():
    config = {
        "p1_char": st.session_state.p1_char,
        "difficulty": st.session_state.difficulty,
        "arena": st.session_state.arena
    }

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
html,body{{margin:0;padding:0;background:#050505;overflow:hidden;user-select:none}}
#game{{position:relative;width:100%;max-width:1000px;margin:auto;aspect-ratio:16/9}}
canvas{{width:100%;height:100%;display:block;background:#000;border:3px solid #333;box-sizing:border-box;touch-action:none}}
#controls{{position:absolute;inset:0;pointer-events:none}}
.pad{{position:absolute;left:15px;bottom:15px;display:grid;grid-template-columns:55px 55px 55px;grid-template-rows:55px 55px 55px;gap:5px;pointer-events:auto}}
.actions{{position:absolute;right:15px;bottom:15px;display:grid;grid-template-columns:60px 60px;grid-template-rows:60px 60px 60px;gap:7px;pointer-events:auto}}
.btn{{display:flex;align-items:center;justify-content:center;border:2px solid white;border-radius:50%;background:rgba(255,255,255,.20);color:white;font-family:Arial;font-weight:bold;font-size:16px;touch-action:none}}
.btn:active{{background:rgba(255,255,255,.60)}}
.up{{grid-column:2;grid-row:1}} .left{{grid-column:1;grid-row:2}}
.down{{grid-column:2;grid-row:3}} .right{{grid-column:3;grid-row:2}}
.punch{{grid-column:1;grid-row:2}} .kick{{grid-column:2;grid-row:2}}
.block{{grid-column:1;grid-row:3}} .special{{grid-column:2;grid-row:3}}
.super{{grid-column:2;grid-row:1;background:rgba(255,30,30,.35)}}
@media (min-width:768px){{#controls{{display:none}}}}
</style>
</head>
<body>
<div id="game">
<canvas id="canvas" width="1000" height="560"></canvas>
<div id="controls">
<div class="pad">
<div class="btn up" data-key="w">▲</div>
<div class="btn left" data-key="a">◀</div>
<div class="btn down" data-key="s">▼</div>
<div class="btn right" data-key="d">▶</div>
</div>
<div class="actions">
<div class="btn super" data-key="i">SUPER</div>
<div class="btn punch" data-key="j">P</div>
<div class="btn kick" data-key="k">K</div>
<div class="btn block" data-key="l">B</div>
<div class="btn special" data-key="u">SP</div>
</div>
</div>
</div>
<script>
const CONFIG={json.dumps(config)};
const canvas=document.getElementById("canvas"),ctx=canvas.getContext("2d");
const W=canvas.width,H=canvas.height,FLOOR=470,GRAVITY=.65;
const keys={{a:false,d:false,w:false,s:false,j:false,k:false,l:false,u:false,i:false}};
window.addEventListener("keydown",e=>{{let k=e.key.toLowerCase();if(keys.hasOwnProperty(k)){{keys[k]=true;e.preventDefault()}}}});
window.addEventListener("keyup",e=>{{let k=e.key.toLowerCase();if(keys.hasOwnProperty(k))keys[k]=false}});
document.querySelectorAll("[data-key]").forEach(btn=>{{
 const key=btn.dataset.key;
 const start=e=>{{e.preventDefault();keys[key]=true}};
 const end=e=>{{e.preventDefault();keys[key]=false}};
 btn.addEventListener("touchstart",start,{{passive:false}});
 btn.addEventListener("touchend",end,{{passive:false}});
 btn.addEventListener("touchcancel",end,{{passive:false}});
 btn.addEventListener("mousedown",start);btn.addEventListener("mouseup",end);btn.addEventListener("mouseleave",end);
}});

const DATA=[
 {{name:"BRAWLER",color:"#ff3333",hp:1000,speed:5,damage:1,defense:1,energy:1}},
 {{name:"ASSASSIN",color:"#33ff33",hp:800,speed:8,damage:.75,defense:.8,energy:1.3}},
 {{name:"TITAN",color:"#ffaa00",hp:1400,speed:3.2,damage:1.55,defense:1.35,energy:.8}},
 {{name:"ZONER",color:"#33ccff",hp:900,speed:5,damage:.9,defense:.9,energy:1.5}}
];

let particles=[],projectiles=[],shake=0,round=1,p1Wins=0,p2Wins=0,timer=99,frame=0;
let state="intro",stateTimer=90,slow=0;

class Fighter{{
 constructor(x,id,player){{
  this.spawnX=x;this.x=x;this.y=FLOOR-115;this.w=55;this.h=115;this.player=player;
  this.id=id;this.data=DATA[id];this.maxHP=this.data.hp;this.hp=this.maxHP;
  this.energy=0;this.facing=player?1:-1;this.vy=0;this.state="idle";this.attack=0;
  this.attackType="";this.cooldown=0;this.hitstun=0;this.combo=0;this.comboTimer=0;
  this.rage=false;this.dashCooldown=0;this.lastHit=false;
 }}
 reset(){{
  this.x=this.spawnX;this.y=FLOOR-this.h;this.vy=0;this.hp=this.maxHP;this.energy=0;
  this.state="idle";this.attack=0;this.cooldown=0;this.hitstun=0;this.combo=0;
  this.comboTimer=0;this.rage=false;this.dashCooldown=0;this.lastHit=false;
 }}
 update(enemy){{
  this.y+=this.vy;this.vy+=GRAVITY;
  if(this.y+this.h>=FLOOR){{this.y=FLOOR-this.h;this.vy=0;if(this.state==="jump")this.state="idle"}}
  if(this.cooldown>0)this.cooldown--;
  if(this.attack>0){{this.attack--;if(this.attack<=0)this.state="idle"}}
  if(this.hitstun>0){{this.hitstun--;if(this.hitstun<=0)this.state="idle"}}
  if(this.comboTimer>0)this.comboTimer--;else this.combo=0;
  if(this.dashCooldown>0)this.dashCooldown--;
  if(!this.rage&&this.hp<=this.maxHP*.25){{this.rage=true;particlesBurst(this.x+this.w/2,this.y+50,35,"#ff2222")}}
  if(this.state!=="attack"&&this.state!=="hit")this.facing=this.x<enemy.x?1:-1;
 }}
 move(dir){{if(this.state==="hit"||this.attack>0)return;this.x+=dir*this.data.speed;this.state="move"}}
 jump(){{if(this.state==="hit"||this.attack>0)return;if(this.y+this.h>=FLOOR-1){{this.vy=-14;this.state="jump"}}}}
 dash(dir){{if(this.dashCooldown>0||this.state==="hit"||this.attack>0)return;this.x+=dir*75;this.dashCooldown=35;particlesBurst(this.x,this.y+80,8,this.data.color)}}
 doAttack(type){{
  if(this.state==="hit"||this.attack>0||this.cooldown>0)return;
  if(type==="special"&&this.energy<25)return;if(type==="super"&&this.energy<100)return;
  this.state="attack";this.attackType=type;
  let rage=this.rage?1.5:1;
  if(type==="punch"){{this.attack=16;this.cooldown=12}}
  else if(type==="kick"){{this.attack=24;this.cooldown=18}}
  else if(type==="special"){{
   this.energy-=25;this.attack=32;this.cooldown=25;
   if(this.id===3)projectiles.push({{x:this.x+(this.facing===1?this.w:-35),y:this.y+45,vx:this.facing*11,damage:75*this.data.damage*rage,life:80,owner:this}});
  }}
  else if(type==="super"){{
   this.energy-=100;this.attack=50;this.cooldown=40;shake=20;slow=35;
   particlesBurst(this.x+this.w/2,this.y+50,45,"#ffff00");
  }}
 }}
 takeDamage(damage,push,attacker){{
  if(this.state==="block"){{
   damage*=.18;this.energy=Math.min(100,this.energy+6*this.data.energy);
   particlesBurst(this.x+this.w/2,this.y+50,8,"#fff");
  }}else{{
   damage/=this.data.defense;this.hp-=damage;this.state="hit";
   this.hitstun=Math.min(35,12+Math.floor(damage/8));this.attack=0;this.comboReset();
   this.x+=-this.facing*push;attacker.combo++;attacker.comboTimer=65;
   attacker.energy=Math.min(100,attacker.energy+8*attacker.data.energy);
   this.energy=Math.min(100,this.energy+10*this.data.energy);
   particlesBurst(this.x+this.w/2,this.y+50,15,"#ffcc66");shake=Math.max(shake,push);
  }}
  this.hp=Math.max(0,this.hp);
 }}
 comboReset(){{this.combo=0;this.comboTimer=0}}
 draw(){{
  let color=this.state==="hit"?"#fff":this.data.color;ctx.save();
  if(this.rage){{ctx.shadowBlur=25;ctx.shadowColor="#f00"}}
  ctx.fillStyle="rgba(0,0,0,.35)";ctx.beginPath();ctx.ellipse(this.x+this.w/2,FLOOR+3,40,9,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle=color;ctx.fillRect(this.x+8,this.y+72,15,43);ctx.fillRect(this.x+32,this.y+72,15,43);
  ctx.fillRect(this.x,this.y+30,this.w,55);ctx.beginPath();ctx.arc(this.x+this.w/2,this.y+18,25,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#111";ctx.fillRect(this.facing===1?this.x+35:this.x+5,this.y+12,8,8);
  if(this.state==="attack"){{
   let reach=this.attackType==="punch"?50:this.attackType==="kick"?75:this.attackType==="special"?100:190;
   let h=this.attackType==="kick"?35:30;
   ctx.fillStyle=this.attackType==="super"?"rgba(255,255,0,.75)":this.attackType==="special"?"rgba(0,200,255,.7)":"rgba(255,50,50,.6)";
   ctx.fillRect(this.facing===1?this.x+this.w-reach*0+this.w-this.w:this.x+this.w,this.y+40,reach,h);
   if(this.facing===-1){{ctx.clearRect(this.x+this.w,this.y+40,reach,h);ctx.fillRect(this.x-reach,this.y+40,reach,h)}}
  }}
  if(this.state==="block"){{ctx.strokeStyle="#00ffff";ctx.lineWidth=6;ctx.beginPath();ctx.arc(this.x+this.w/2,this.y+55,48,0,Math.PI*2);ctx.stroke()}}
  ctx.restore();
 }}
}}

let p1=new Fighter(150,CONFIG.p1_char,true);
let p2=new Fighter(795,Math.floor(Math.random()*4),false);
let aiCooldown=0;

function particlesBurst(x,y,n,color){{for(let i=0;i<n;i++)particles.push({{x,y,vx:(Math.random()-.5)*12,vy:(Math.random()-.5)*12,life:20+Math.random()*30,color}})}}
function updateParticles(){{for(let i=particles.length-1;i>=0;i--){{let p=particles[i];p.x+=p.vx;p.y+=p.vy;p.vx*=.96;p.vy*=.96;p.life--;if(p.life<=0)particles.splice(i,1)}}}}
function drawParticles(){{for(const p of particles){{ctx.globalAlpha=Math.max(0,p.life/40);ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y,5,5)}}ctx.globalAlpha=1}}
function updateProjectiles(){{
 for(let i=projectiles.length-1;i>=0;i--){{
  let p=projectiles[i];p.x+=p.vx;p.life--;ctx.fillStyle="#00ffff";ctx.shadowBlur=20;ctx.shadowColor="#00ffff";
  ctx.beginPath();ctx.arc(p.x,p.y,14,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
  let target=p.owner===p1?p2:p1;
  if(p.x<target.x+target.w&&p.x+20>target.x&&p.y<target.y+target.h&&p.y+20>target.y){{target.takeDamage(p.damage,12,p.owner);projectiles.splice(i,1);continue}}
  if(p.life<=0||p.x<-50||p.x>W+50)projectiles.splice(i,1);
 }}
}}
function attackCollision(a,d){{
 if(a.state!=="attack")return;if(a.attackType==="special"&&a.id===3)return;
 let active=a.attackType==="punch"?a.attack>=8:a.attackType==="kick"?a.attack>=10:a.attackType==="special"?a.attack>=15:a.attack>=20;
 if(!active)return;
 let reach=a.attackType==="punch"?50:a.attackType==="kick"?75:a.attackType==="special"?120:190;
 let x=a.facing===1?a.x+a.w:a.x-reach,y=a.y+30;
 if(x<d.x+d.w&&x+reach>d.x&&y<d.y+d.h&&y+60>d.y){{
  if(!a.lastHit){{
   let base=a.attackType==="punch"?28:a.attackType==="kick"?48:a.attackType==="special"?80:260;
   d.takeDamage(base*a.data.damage*(a.rage?1.5:1),a.attackType==="super"?30:a.attackType==="kick"?14:7,a);a.lastHit=true;
  }}
 }}else a.lastHit=false;
}}
function playerInput(){{
 if(p1.state==="hit"||p1.attack>0)return;
 if(keys.l){{p1.state="block";return}}
 if(keys.w)p1.jump();if(keys.a)p1.move(-1);if(keys.d)p1.move(1);
 if(keys.j)p1.doAttack("punch");else if(keys.k)p1.doAttack("kick");else if(keys.u)p1.doAttack("special");else if(keys.i)p1.doAttack("super");
}}
function cpuAI(){{
 if(p2.state==="hit"||p2.attack>0)return;
 const difficulty=CONFIG.difficulty,dx=p1.x-p2.x,dist=Math.abs(dx);
 if(aiCooldown>0){{aiCooldown--;return}}
 let chance=.12+difficulty*.13;
 if(Math.random()<chance){{
  if(dist>150)p2.move(dx>0?1:-1);
  else if(dist>85){{if(Math.random()<.4)p2.move(dx>0?1:-1);if(p2.id===3&&p2.energy>=25&&Math.random()<.35)p2.doAttack("special")}}
  else{{let r=Math.random();if(r<.4)p2.doAttack("punch");else if(r<.7)p2.doAttack("kick");else if(p2.energy>=25&&r<.9)p2.doAttack("special");else if(p2.energy>=100)p2.doAttack("super")}}
 }}
 if(difficulty>=2&&p1.state==="attack"&&dist<130&&Math.random()<.55)p2.state="block";
 aiCooldown=Math.max(5,20-difficulty*4);
}}
function clamp(){{p1.x=Math.max(0,Math.min(W-p1.w,p1.x));p2.x=Math.max(0,Math.min(W-p2.w,p2.x))}}

function drawBackground(){{
 let arena=CONFIG.arena;
 if(arena===0){{
  let g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,"#05052b");g.addColorStop(1,"#15001f");ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  for(let i=0;i<14;i++){{let h=100+(i*47)%180;ctx.fillStyle="#090919";ctx.fillRect(i*80,FLOOR-h,65,h);ctx.fillStyle="#ffff55";for(let y=FLOOR-h+20;y<FLOOR;y+=30)if((i+y)%3===0)ctx.fillRect(i*80+15,y,8,10)}}
 }}else if(arena===1){{ctx.fillStyle="#33200f";ctx.fillRect(0,0,W,H);ctx.fillStyle="#70451e";for(let x=0;x<W;x+=80)ctx.fillRect(x,0,3,FLOOR)}}
 else if(arena===2){{ctx.fillStyle="#00151e";ctx.fillRect(0,0,W,H);ctx.strokeStyle="#00ffff";ctx.lineWidth=1;for(let x=0;x<W;x+=50){{ctx.beginPath();ctx.moveTo(x,FLOOR);ctx.lineTo(W/2+(x-W/2)*.2,260);ctx.stroke()}}for(let y=270;y<FLOOR;y+=30){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}}}}
 else{{ctx.fillStyle="#220022";ctx.fillRect(0,0,W,H);ctx.strokeStyle="#ff00ff";ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,FLOOR);ctx.lineTo(W,FLOOR);ctx.stroke()}}
 ctx.fillStyle="#161616";ctx.fillRect(0,FLOOR,W,H-FLOOR);
}}
function bar(x,y,w,h,value,max,color){{ctx.fillStyle="#111";ctx.fillRect(x,y,w,h);ctx.fillStyle=color;ctx.fillRect(x,y,Math.max(0,w*(value/max)),h);ctx.strokeStyle="#fff";ctx.lineWidth=2;ctx.strokeRect(x,y,w,h)}}
function drawUI(){{
 bar(40,35,360,25,p1.hp,p1.maxHP,"#20ff40");bar(600,35,360,25,p2.hp,p2.maxHP,"#20ff40");
 bar(40,67,250,10,p1.energy,100,"#00d9ff");bar(710,67,250,10,p2.energy,100,"#00d9ff");
 ctx.fillStyle="#fff";ctx.font="16px Arial";ctx.fillText(p1.data.name,40,27);ctx.fillText(p2.data.name,830,27);
 ctx.font="bold 30px Arial";ctx.textAlign="center";ctx.fillText(timer,W/2,58);ctx.font="bold 18px Arial";ctx.fillText("ROUND "+round,W/2,90);ctx.textAlign="left";
 ctx.fillStyle="#ffd700";ctx.font="18px Arial";ctx.fillText("WINS: "+p1Wins,40,105);ctx.fillText("WINS: "+p2Wins,850,105);
 if(p1.combo>=2){{ctx.fillStyle="#ffff00";ctx.font="bold 25px Arial";ctx.fillText(p1.combo+" HIT COMBO!",45,145)}}
 if(p2.combo>=2){{ctx.fillStyle="#ffff00";ctx.font="bold 25px Arial";ctx.fillText(p2.combo+" HIT COMBO!",650,145)}}
 if(state!=="fighting"){{
  ctx.fillStyle="rgba(0,0,0,.55)";ctx.fillRect(0,0,W,H);ctx.textAlign="center";ctx.font="bold 48px Arial";ctx.fillStyle="#fff";
  if(state==="intro")ctx.fillText("ROUND "+round+" • FIGHT!",W/2,H/2);
  if(state==="ko")ctx.fillText("K.O!",W/2,H/2);
  if(state==="time")ctx.fillText("TIME OVER",W/2,H/2);
  if(state==="gameover")ctx.fillText(p1Wins>p2Wins?"YOU WIN!":"YOU LOSE!",W/2,H/2);
  ctx.textAlign="left";
 }}
}}
function nextRound(){{round++;p1.reset();p2.reset();timer=99;frame=0;state="intro";stateTimer=75;particles=[];projectiles=[]}}
function loop(){{
 requestAnimationFrame(loop);
 if(slow>0){{slow--;if(slow%3!==0)return}}
 ctx.save();
 if(shake>0){{ctx.translate((Math.random()-.5)*shake,(Math.random()-.5)*shake);shake*=.86;if(shake<.5)shake=0}}
 drawBackground();
 if(state==="intro"){{stateTimer--;if(stateTimer<=0)state="fighting"}}
 else if(state==="fighting"){{
  frame++;if(frame%60===0)timer--;playerInput();cpuAI();p1.update(p2);p2.update(p1);
  if(Math.abs((p1.x+p1.w/2)-(p2.x+p2.w/2))<45){{if(p1.x<p2.x){{p1.x-=2;p2.x+=2}}else{{p1.x+=2;p2.x-=2}}}}
  attackCollision(p1,p2);attackCollision(p2,p1);updateProjectiles();
  if(p1.hp<=0||p2.hp<=0){{state="ko";stateTimer=100;if(p1.hp<=0)p2Wins++;else p1Wins++}}
  else if(timer<=0){{state="time";stateTimer=100;if(p1.hp>p2.hp)p1Wins++;else if(p2.hp>p1.hp)p2Wins++}}
 }}
 else if(state==="ko"||state==="time"){{stateTimer--;if(stateTimer<=0)nextRound()}}
 p1.draw();p2.draw();updateParticles();drawParticles();clamp();ctx.restore();drawUI();
}}
loop();
</script>
</body>
</html>
"""

def menu():
    st.title("🔥 STREAMLIT ARCADE FIGHTER 2D 🔥")
    st.markdown("### 🥊 Arcade Fighting Game")
    st.divider()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        if st.button("🥊 FIGHT!",use_container_width=True):
            st.session_state.page="game";st.rerun()
        if st.button("👤 CHARACTER SELECT",use_container_width=True):
            st.session_state.page="character";st.rerun()
        if st.button("⚙️ SETTINGS",use_container_width=True):
            st.session_state.page="settings";st.rerun()
        if st.button("🎮 HOW TO PLAY",use_container_width=True):
            st.session_state.page="help";st.rerun()

def character():
    st.title("👤 SELECT YOUR FIGHTER")
    cols=st.columns(4)
    for i,char in enumerate(CHARACTERS):
        with cols[i]:
            st.markdown(f"<h2 style='color:{char['color']}'>{char['name']}</h2>",unsafe_allow_html=True)
            st.write(char["desc"])
            if st.button("CHỌN",key=f"char_{i}",use_container_width=True):
                st.session_state.p1_char=i
                st.success(f"Đã chọn {char['name']}")
    st.divider()
    if st.button("← MENU"):
        st.session_state.page="menu";st.rerun()

def settings():
    st.title("⚙️ SETTINGS")
    st.session_state.difficulty=st.selectbox("CPU Difficulty",range(4),format_func=lambda x:DIFFICULTIES[x],index=st.session_state.difficulty)
    st.session_state.arena=st.selectbox("Arena",range(4),format_func=lambda x:ARENAS[x],index=st.session_state.arena)
    st.info("🏆 Không giới hạn số round — trận đấu tiếp tục cho đến khi bạn thoát.")
    if st.button("💾 SAVE & MENU"):
        st.session_state.page="menu";st.rerun()

def help_page():
    st.title("🎮 HOW TO PLAY")
    st.markdown("""
### 🖥️ PC
| Phím | Chức năng |
|---|---|
| A / D | Di chuyển |
| W | Nhảy |
| S | Cúi |
| J | Đấm |
| K | Đá |
| L | Block |
| U | Special |
| I | Super |

### 📱 Mobile
Dùng D-Pad bên trái và các nút P / K / B / SP / SUPER bên phải.

### ⚡ Năng lượng
25 Energy → Special.  
100 Energy → Super.

### 🔥 Rage
HP dưới 25% → Rage Mode, sát thương tăng 1.5x.

### ♾️ Infinite Round
Round tăng mãi: 1 → 2 → 3 → 4 → 5 → ...
""")
    if st.button("← MENU"):
        st.session_state.page="menu";st.rerun()

def game():
    st.markdown("### 🥊 ARCADE FIGHTER")
    components.html(get_game_html(),height=600,scrolling=False)
    st.caption("PC: A/D/W/S + J/K/L/U/I • Mobile: dùng các nút trên màn hình")
    if st.button("← EXIT TO MENU"):
        st.session_state.page="menu";st.rerun()

if st.session_state.page=="menu":
    menu()
elif st.session_state.page=="character":
    character()
elif st.session_state.page=="settings":
    settings()
elif st.session_state.page=="help":
    help_page()
elif st.session_state.page=="game":
    game()
