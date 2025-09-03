const captureBgBtn = document.getElementById('captureBgBtn');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const videoFeed = document.getElementById('videoFeed');
const sensitivityRange = document.getElementById('sensitivityRange');
const sensitivityValue = document.getElementById('sensitivityValue');
const houseSelector = document.getElementById('houseSelector');
const sparkleDiv = document.getElementById('sparkle');
const startMagic = document.getElementById('startMagic');
const stopMagic = document.getElementById('stopMagic');

let cloakRunning = false;
let bgCaptured = false;

captureBgBtn.addEventListener('click', () => {
  fetch('/capture_background', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        bgCaptured = true;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        captureBgBtn.disabled = true;
        alert('Background captured! Stand in front of your cloak and cast the spell.');
      }
    });
});

startBtn.addEventListener('click', () => {
  if (bgCaptured && !cloakRunning) {
    videoFeed.src = '/video_feed?d=' + new Date().getTime();
    cloakRunning = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    if (startMagic) startMagic.play();
    sparkleDiv.style.display = 'block';
    setTimeout(() => { sparkleDiv.style.display = 'none'; }, 1600);
  }
});

stopBtn.addEventListener('click', () => {
  if (cloakRunning) {
    videoFeed.src = '/static/placeholder.jpg'; // Use magical placeholder here!
    cloakRunning = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (stopMagic) stopMagic.play();
  }
});

sensitivityRange.addEventListener('input', () => {
  const val = parseInt(sensitivityRange.value);
  sensitivityValue.textContent = val;
  fetch('/set_sensitivity', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({sensitivity: val})
  }).then(res => res.json());
});

houseSelector.addEventListener('change', () => {
  document.body.className = houseSelector.value;
});
