const missionList = {
  tree100: {
    id: 'tree100',
    title: '100 Tree Plant',
    difficulty: 'Hard',
    difficultyClass: 'hard',
    points: 100,
    maxProgress: 100,
    description: 'Plant 100 trees in your area, campus, or community and help restore the environment.',
    steps: [
      'Identify a suitable place for planting trees with local support.',
      'Plant as many saplings as possible in a planned and safe area.',
      'Care for the trees regularly so they can grow and survive.'
    ]
  },
  clean21: {
    id: 'clean21',
    title: '21 Day Clean',
    difficulty: 'Medium',
    difficultyClass: 'medium',
    points: 75,
    maxProgress: 21,
    description: 'Take part in a 21-day clean drive and keep your local area, campus, or street cleaner.',
    steps: [
      'Join or organize a daily cleanup in your area.',
      'Collect litter responsibly and separate waste where possible.',
      'Keep the community clean for 21 consecutive days.'
    ]
  },
  lightoff: {
    id: 'lightoff',
    title: 'Light Off',
    difficulty: 'Easy',
    difficultyClass: 'easy',
    points: 50,
    maxProgress: 10,
    description: 'Switch off unused lights in school or any other location to save electricity and reduce waste.',
    steps: [
      'Turn off lights in empty classrooms, rooms, or corridors.',
      'Use natural daylight whenever it is enough.',
      'Encourage others to switch off lights when not needed.'
    ]
  }
};

const params = new URLSearchParams(window.location.search);
const missionId = params.get('mission') || 'tree100';
const mission = missionList[missionId] || missionList.tree100;

const missionProgressData = JSON.parse(localStorage.getItem('missionProgress') || '{}');
const completedMissions = JSON.parse(localStorage.getItem('completedMissions') || '[]');
const missionPageMessage = document.getElementById('missionPageMessage');
const detailButton = document.getElementById('missionDetailButton');

const titleEl = document.getElementById('missionDetailTitle');
const difficultyEl = document.getElementById('missionDetailDifficulty');
const rewardEl = document.getElementById('missionDetailReward');
const descriptionEl = document.getElementById('missionDetailDescription');
const stepsEl = document.getElementById('missionDetailSteps');
const rewardBigEl = document.getElementById('missionDetailRewardBig');
const progressCount = document.getElementById('missionProgressCount');
const progressText = document.getElementById('missionProgressText');

function getMissionProgress() {
  return Number(missionProgressData[mission.id] || 0);
}

function isMissionCompleted() {
  return completedMissions.includes(mission.id);
}

function awardMissionPointsOnce() {
  if (isMissionCompleted()) {
    return false;
  }

  completedMissions.push(mission.id);
  localStorage.setItem('completedMissions', JSON.stringify(completedMissions));

  const missionHistory = JSON.parse(localStorage.getItem('missionHistory') || '[]');
  const savedPoints = Number(localStorage.getItem('studentPoints') || 0);

  missionHistory.push({
    id: mission.id,
    points: mission.points,
    completedAt: new Date().toISOString()
  });

  localStorage.setItem('missionHistory', JSON.stringify(missionHistory));
  localStorage.setItem('studentPoints', String(savedPoints + mission.points));
  return true;
}

function updateMissionProgress() {
  const currentProgress = getMissionProgress();
  const isCompleted = currentProgress >= mission.maxProgress || isMissionCompleted();

  progressCount.textContent = `${currentProgress} / ${mission.maxProgress}`;
  progressText.textContent = isCompleted
    ? 'All steps completed'
    : `${currentProgress} ${currentProgress === 1 ? 'step' : 'steps'} tracked`;
}

function renderMission() {
  titleEl.textContent = mission.title;
  difficultyEl.textContent = mission.difficulty;
  difficultyEl.className = `difficulty ${mission.difficultyClass}`;
  rewardEl.textContent = `+${mission.points} points`;
  rewardBigEl.textContent = `+${mission.points}`;
  descriptionEl.textContent = mission.description;

  stepsEl.innerHTML = '';
  mission.steps.forEach(function (step) {
    const item = document.createElement('li');
    item.textContent = step;
    stepsEl.appendChild(item);
  });

  const currentProgress = getMissionProgress();
  const isCompleted = currentProgress >= mission.maxProgress || isMissionCompleted();

  detailButton.disabled = isCompleted;
  detailButton.textContent = isCompleted ? 'Goal reached' : 'Complete mission';
  missionPageMessage.textContent = isCompleted
    ? `Goal reached! You earned ${mission.points} points.`
    : currentProgress > 0 ? `Progress: ${currentProgress}/${mission.maxProgress}` : '';

  updateMissionProgress();
}

detailButton.addEventListener('click', function () {
  const currentProgress = getMissionProgress();
  const nextProgress = Math.min(currentProgress + 1, mission.maxProgress);
  missionProgressData[mission.id] = nextProgress;

  if (nextProgress >= mission.maxProgress) {
    awardMissionPointsOnce();
  }

  localStorage.setItem('missionProgress', JSON.stringify(missionProgressData));

  const isCompleted = isMissionCompleted() || nextProgress >= mission.maxProgress;
  detailButton.disabled = isCompleted;
  detailButton.textContent = isCompleted ? 'Goal reached' : 'Complete mission';
  missionPageMessage.textContent = isCompleted
    ? `Goal reached! You earned ${mission.points} points.`
    : `Progress: ${nextProgress}/${mission.maxProgress}`;

  updateMissionProgress();
});

renderMission();
