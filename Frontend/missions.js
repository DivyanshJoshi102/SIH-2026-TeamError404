// Completed missions aur points browser me save karta hai, taaki refresh ke baad data rahe.
const missionButtons = document.querySelectorAll('.mission-complete-button');
const missionPageMessage = document.getElementById('missionPageMessage');
const missionCountLabel = document.getElementById('missionCountLabel');
const savedMissions = JSON.parse(localStorage.getItem('completedMissions') || '[]');
const missionHistory = JSON.parse(localStorage.getItem('missionHistory') || '[]');
const missionProgress = JSON.parse(localStorage.getItem('missionProgress') || '{}');
let savedPoints = Number(localStorage.getItem('studentPoints') || 0);

function updateMissionCount() {
  const completedCount = savedMissions.length;
  missionCountLabel.textContent = `${completedCount} / 3 completed`;
}

missionButtons.forEach(function (button) {
  const missionId = button.dataset.mission;
  const missionLimit = {
    tree100: 100,
    clean21: 21,
    lightoff: 10
  };
  const currentProgress = Number(missionProgress[missionId] || 0);
  const missionCompleted = savedMissions.includes(missionId) || currentProgress >= (missionLimit[missionId] || 10);

  if (missionCompleted) {
    button.disabled = true;
    button.textContent = 'Goal reached';
  } else if (currentProgress > 0) {
    button.textContent = `Progress ${currentProgress}/${missionLimit[missionId] || 10}`;
  }

  button.addEventListener('click', function () {
    const missionId = button.dataset.mission;
    const missionPoints = Number(button.dataset.points);
    const maxProgress = {
      tree100: 100,
      clean21: 21,
      lightoff: 10
    }[missionId] || 10;
    const currentProgress = Number(missionProgress[missionId] || 0);
    const nextProgress = Math.min(currentProgress + 1, maxProgress);

    missionProgress[missionId] = nextProgress;
    localStorage.setItem('missionProgress', JSON.stringify(missionProgress));

    if (nextProgress >= maxProgress && !savedMissions.includes(missionId)) {
      savedMissions.push(missionId);
      localStorage.setItem('completedMissions', JSON.stringify(savedMissions));
      missionHistory.push({ id: missionId, points: missionPoints, completedAt: new Date().toISOString() });
      localStorage.setItem('missionHistory', JSON.stringify(missionHistory));
      savedPoints += missionPoints;
      localStorage.setItem('studentPoints', String(savedPoints));
    }

    const missionCompleted = nextProgress >= maxProgress || savedMissions.includes(missionId);
    button.disabled = missionCompleted;
    button.textContent = missionCompleted ? 'Goal reached' : `Progress ${nextProgress}/${maxProgress}`;
    missionPageMessage.textContent = missionCompleted
      ? `Great work! You earned ${missionPoints} points.`
      : `Progress updated: ${nextProgress}/${maxProgress}`;
    updateMissionCount();
  });
});

updateMissionCount();
