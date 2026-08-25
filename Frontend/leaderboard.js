// Saved student data aur mission history ko leaderboard ke liye load karta hai.
const filterButtons = document.querySelectorAll('.filter-button');
const account = JSON.parse(localStorage.getItem('greenQuestAccount') || 'null');
const missionHistory = JSON.parse(localStorage.getItem('missionHistory') || '[]');
const allTimePoints = Number(localStorage.getItem('studentPoints') || 0);
const studentName = account ? account.name : 'Student';

const sampleStudents = {
  week: [
    { name: 'Rohan Sharma', points: 920 }, { name: 'Meera Singh', points: 840 },
    { name: 'Kavya Iyer', points: 790 }, { name: 'Aarav Patel', points: 760 },
    { name: 'Diya Nair', points: 730 }, { name: 'Arjun Mehta', points: 710 }, { name: 'Kabir Khan', points: 640 }
  ],
  month: [
    { name: 'Meera Singh', points: 1580 }, { name: 'Rohan Sharma', points: 1490 },
    { name: 'Aarav Patel', points: 1370 }, { name: 'Kavya Iyer', points: 1290 },
    { name: 'Diya Nair', points: 1210 }, { name: 'Kabir Khan', points: 1100 }, { name: 'Arjun Mehta', points: 1040 }
  ],
  all: [
    { name: 'Rohan Sharma', points: 4200 }, { name: 'Kavya Iyer', points: 3980 },
    { name: 'Meera Singh', points: 3850 }, { name: 'Aarav Patel', points: 3620 },
    { name: 'Diya Nair', points: 3410 }, { name: 'Arjun Mehta', points: 3290 }, { name: 'Kabir Khan', points: 3150 }
  ]
};

// Selected period ke days ke andar complete hue missions ke points jodta hai.
function getStudentPoints(period) {
  if (period === 'all') {
    return allTimePoints;
  }

  const days = period === 'week' ? 7 : 30;
  const limit = Date.now() - days * 24 * 60 * 60 * 1000;
  return missionHistory
    .filter(function (mission) { return new Date(mission.completedAt).getTime() >= limit; })
    .reduce(function (total, mission) { return total + mission.points; }, 0);
}

// Student name ke first letters ko simple avatar me show karta hai.
function getInitials(name) {
  return name.split(' ').map(function (word) { return word[0]; }).join('').slice(0, 2).toUpperCase();
}

// Podium ke top three cards ko sorted ranking ke according update karta hai.
function renderPodium(ranking) {
  const podiumPlaces = [
    { name: 'secondName', points: 'secondPoints', avatar: 'secondAvatar' },
    { name: 'firstName', points: 'firstPoints', avatar: 'firstAvatar' },
    { name: 'thirdName', points: 'thirdPoints', avatar: 'thirdAvatar' }
  ];
  const podiumRanking = [ranking[1], ranking[0], ranking[2]];

  podiumPlaces.forEach(function (place, index) {
    const student = podiumRanking[index];
    document.getElementById(place.name).textContent = student.name;
    document.getElementById(place.points).textContent = `${student.points} pts`;
    document.getElementById(place.avatar).textContent = getInitials(student.name);
  });
}

// Full ranking list banata hai aur current student ko highlight karta hai.
function renderRanking(period) {
  const currentStudent = { name: studentName, points: getStudentPoints(period), current: true };
  const ranking = sampleStudents[period].filter(function (student) { return student.name !== studentName; });
  ranking.push(currentStudent);
  ranking.sort(function (first, second) { return second.points - first.points; });
  renderPodium(ranking);

  const rankingList = document.getElementById('rankingList');
  rankingList.innerHTML = '<div class="ranking-row ranking-heading"><span>Rank &amp; student</span><span>Points</span></div>';
  ranking.slice(0, 8).forEach(function (student, index) {
    const row = document.createElement('div');
    row.className = student.current ? 'ranking-row your-ranking' : 'ranking-row';
    const name = document.createElement('span');
    const rank = document.createElement('b');
    rank.textContent = String(index + 1).padStart(2, '0');
    name.append(rank, ` ${student.name}`);
    if (student.current) {
      const label = document.createElement('small');
      label.textContent = 'You';
      name.appendChild(label);
    }
    const points = document.createElement('strong');
    points.textContent = student.points;
    row.append(name, points);
    rankingList.appendChild(row);
  });
}

// Saved signup name aur initial period ki ranking load karta hai.
renderRanking('week');

filterButtons.forEach(function (button) {
  button.addEventListener('click', function () {
    filterButtons.forEach(function (item) {
      item.classList.remove('active-filter');
    });
    button.classList.add('active-filter');
    const period = button.textContent === 'This month' ? 'month' : button.textContent === 'All time' ? 'all' : 'week';
    renderRanking(period);
  });
});
