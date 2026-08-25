// Completed missions aur points browser me save karta hai, taaki refresh ke baad data rahe.
const missionButtons = document.querySelectorAll('.mission-complete-button');
const missionPageMessage = document.getElementById('missionPageMessage');
const savedMissions = JSON.parse(localStorage.getItem('completedMissions') || '[]');
const missionHistory = JSON.parse(localStorage.getItem('missionHistory') || '[]');
let savedPoints = Number(localStorage.getItem('studentPoints') || 0);

// Pehle se complete missions ko page par disabled dikhata hai.
missionButtons.forEach(function (button) {
  if (savedMissions.includes(button.dataset.mission)) {
    button.textContent = 'Mission completed';
    button.disabled = true;
  }

  button.addEventListener('click', function () {
    const missionId = button.dataset.mission;
    const missionPoints = Number(button.dataset.points);

    if (savedMissions.includes(missionId)) {
      return;
    }

    savedMissions.push(missionId);
    savedPoints += missionPoints;
    missionHistory.push({ id: missionId, points: missionPoints, completedAt: new Date().toISOString() });
    localStorage.setItem('completedMissions', JSON.stringify(savedMissions));
    localStorage.setItem('missionHistory', JSON.stringify(missionHistory));
    localStorage.setItem('studentPoints', savedPoints);

    button.textContent = 'Mission completed';
    button.disabled = true;
    missionPageMessage.textContent = `Great work! You earned ${missionPoints} points.`;
  });
});
