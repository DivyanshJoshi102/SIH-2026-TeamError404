// Saved account aur missions ko dashboard par load karta hai.
const account = JSON.parse(localStorage.getItem('greenQuestAccount') || 'null');
const completedMissions = JSON.parse(localStorage.getItem('completedMissions') || '[]');
const studentPoints = Number(localStorage.getItem('studentPoints') || 0);
const missionDetails = {
  walk: { name: 'Walk or cycle', points: 50 },
  plastic: { name: 'Plastic-free day', points: 75 },
  plant: { name: 'Plant a friend', points: 100 }
};

// Account available ho to signup wala naam welcome heading me dikhata hai.
if (account) {
  document.getElementById('dashboardName').textContent = account.name.split(' ')[0];
}

// Points, mission count aur level progress saved data ke according update karta hai.
document.getElementById('dashboardPoints').textContent = studentPoints;
document.getElementById('dashboardMissionCount').textContent = completedMissions.length;
document.getElementById('dashboardWeeklyPoints').textContent = studentPoints > 0 ? `+${studentPoints} this week` : 'Start your first mission';
document.getElementById('dashboardProgressText').textContent = `${studentPoints} / 1,000 points to next level`;
document.getElementById('dashboardProgressBar').firstElementChild.style.width = `${Math.min(studentPoints / 10, 100)}%`;
document.getElementById('dashboardProgressBar').setAttribute('aria-label', `${Math.min(studentPoints / 10, 100)} percent progress`);

// Completed missions ki list ko saved mission IDs se banata hai.
const completedMissionList = document.getElementById('completed-missions');
completedMissions.forEach(function (missionId) {
  const mission = missionDetails[missionId];
  const listItem = document.createElement('li');
  listItem.innerHTML = `<span>${mission.name}<br><small>Completed mission</small></span><strong>+${mission.points}</strong>`;
  completedMissionList.appendChild(listItem);
});

// Start button click hone par missions page open karta hai.
const missionButtons = document.querySelectorAll('.mission-action');
const dashboardMessage = document.getElementById('dashboardMessage');

missionButtons.forEach(function (button) {
  button.addEventListener('click', function () {
    window.location.href = 'missions.html';
  });
});
