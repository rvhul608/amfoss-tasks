const canvas = document.getElementById("canvas1");
const ctx = canvas.getContext("2d");
const drawaudio = document.getElementById("drawaudio");
drawaudio.loop = true;
const bg = new Image();
bg.src = "background.jpg";
function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  drawBackground();
}
function drawBackground() {
  ctx.drawImage(bg, 0, 0, canvas.width, canvas.height);
}
function drawCenter(){
    const centerCanvasX = canvas.width / 2;
    const centerCanvasY = canvas.height / 2;

    ctx.fillStyle = 'red'; 
    ctx.beginPath();
    ctx.arc(centerCanvasX, centerCanvasY, 10, 0, Math.PI * 2);
    ctx.fill();
}
function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground();
  drawCenter();
}
bg.onload = () => {
  resizeCanvas();
};
window.addEventListener("resize", resizeCanvas);
let drawing = false;
let points = [];
let drawColor = "yellow"; 
let highestScore = 0;
canvas.addEventListener("mousedown", (e) => {
  drawing = true;
  points = [];
  clearCanvas();
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  points.push({ x, y });
  ctx.beginPath();
  ctx.moveTo(x, y);
  drawaudio.currentTime = 0;
  drawaudio.play();
});
canvas.addEventListener("mouseup", () => {
  drawing = false;
  ctx.closePath();
  checkCircle();
  drawaudio.pause();
});
canvas.addEventListener("mousemove", (e) => {
  if (!drawing) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  points.push({ x, y });
  ctx.lineTo(x, y);
  ctx.strokeStyle = drawColor;
  ctx.lineWidth = 2;
  ctx.stroke();
});
function checkCircle() {
  if (points.length < 10) return;
  let sumX = 0, sumY = 0;
  points.forEach(p => {
    sumX += p.x;
    sumY += p.y;
  });
  const centerX = sumX / points.length;
  const centerY = sumY / points.length;
  let sumR = 0;
  points.forEach(p => {
    const dx = p.x - centerX;
    const dy = p.y - centerY;
    sumR += Math.sqrt(dx*dx + dy*dy);
  });
  const avgR = sumR / points.length;
  const fixedX = canvas.width / 2;
  const fixedY = canvas.height / 2;
  const dx = fixedX - centerX;
  const dy = fixedY - centerY;
  const dist = Math.sqrt(dx*dx + dy*dy);

  if (dist > avgR) {
    alert("The circle does not contain the center point ");
    return;
  }
  let variance = 0;
  points.forEach(p => {
    const dx = p.x - centerX;
    const dy = p.y - centerY;
    const r = Math.sqrt(dx*dx + dy*dy);
    variance += Math.abs(r - avgR);
  });
  variance /= points.length;

  const raw = 100 - variance;
  const score = Math.max(0, raw);
  if (score > highestScore) {
    highestScore = score;
  }

  document.getElementById("result").innerText =
    `Your score is: ${score.toFixed(2)} / 100 - Highest score: ${highestScore.toFixed(2)} / 100`;
  ctx.strokeStyle = "red";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(centerX, centerY, avgR, 0, Math.PI * 2);
  ctx.stroke();
}
