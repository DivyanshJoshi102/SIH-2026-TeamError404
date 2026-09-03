// Saved account aur missions ko dashboard par load karta hai.
const account = JSON.parse(localStorage.getItem('greenQuestAccount') || 'null');
const savedPoints = Number(localStorage.getItem('studentPoints') || 0);
const completedMissions = JSON.parse(localStorage.getItem('completedMissions') || '[]');
const dailyMissionPoints = { bottle: 20, waste: 30, plant: 50 };

if (account) {
  document.getElementById('dashboardName').textContent = account.name.split(' ')[0];
}

document.getElementById('dashboardProgressText').textContent = `${savedPoints} / 1,000 points to next level`;
document.getElementById('dashboardProgressBar').firstElementChild.style.width = `${Math.min(savedPoints / 10, 100)}%`;
document.getElementById('impactActions').textContent = completedMissions.length + Number(localStorage.getItem('completedDailyMissions') ? JSON.parse(localStorage.getItem('completedDailyMissions')).length : 0);

document.querySelectorAll('.start-daily').forEach(function (button) {
  button.addEventListener('click', function () {
    const missionId = button.dataset.mission;
    const completedDaily = JSON.parse(localStorage.getItem('completedDailyMissions') || '[]');
    if (!completedDaily.includes(missionId)) {
      completedDaily.push(missionId);
      localStorage.setItem('completedDailyMissions', JSON.stringify(completedDaily));
      localStorage.setItem('studentPoints', String(Number(localStorage.getItem('studentPoints') || 0) + dailyMissionPoints[missionId]));
    }
    button.textContent = 'Mission complete';
    button.disabled = true;
    document.getElementById('dashboardMessage').textContent = `Great work! You earned ${dailyMissionPoints[missionId]} XP.`;
  });
});

const streakCalendar = document.getElementById('streakCalendar');
for (let day = 1; day <= 21; day += 1) {
  const dayCell = document.createElement('span');
  dayCell.textContent = day;
  dayCell.className = day <= 7 ? 'complete-day' : '';
  dayCell.setAttribute('aria-label', `Day ${day}${day <= 7 ? ', completed' : ', remaining'}`);
  streakCalendar.appendChild(dayCell);
}

const proofPhoto = document.getElementById('proofPhoto');
proofPhoto.addEventListener('change', function () {
  const file = proofPhoto.files[0];
  if (!file) return;
  document.getElementById('proofLabel').textContent = file.name;
  const preview = document.getElementById('proofPreview');
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
});

document.getElementById('submitProof').addEventListener('click', function () {
  document.getElementById('proofStatus').textContent = 'Pending';
  document.getElementById('proofStatus').className = 'status-pill pending';
  document.getElementById('proofMessage').textContent = 'Proof submitted. A teacher will review it soon.';
});

document.querySelectorAll('.map-marker').forEach(function (marker) {
  marker.addEventListener('click', function () {
    document.getElementById('mapTooltip').textContent = `${marker.dataset.city}: ${marker.dataset.actions} actions completed`;
  });
});

document.querySelectorAll('.approve-button, .reject-button').forEach(function (button) {
  button.addEventListener('click', function () {
    const submission = button.closest('article');
    submission.classList.add('reviewed');
    submission.querySelector('.approve-button').disabled = true;
    submission.querySelector('.reject-button').disabled = true;
    document.getElementById('teacherMessage').textContent = button.classList.contains('approve-button')
      ? 'Submission approved and XP awarded.'
      : 'Submission rejected with feedback requested.';
  });
});

function updateConnectionStatus() {
  const indicator = document.getElementById('offline-sync');
  indicator.className = navigator.onLine ? 'offline-indicator' : 'offline-indicator is-offline';
  indicator.innerHTML = `<span></span>${navigator.onLine ? 'All progress synced' : 'Offline Mode - Progress saved locally'}`;
  if (navigator.onLine) {
    indicator.classList.add('is-syncing');
    indicator.innerHTML = '<span></span>Syncing...';
    window.setTimeout(function () { indicator.className = 'offline-indicator'; indicator.innerHTML = '<span></span>All progress synced'; }, 1200);
  }
}

window.addEventListener('online', updateConnectionStatus);
window.addEventListener('offline', updateConnectionStatus);
updateConnectionStatus();
