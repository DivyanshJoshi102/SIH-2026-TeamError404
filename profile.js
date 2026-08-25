// Saved account aur progress ko profile page par load karta hai.
const profileForm = document.getElementById('profileForm');
const profileMessage = document.getElementById('profileMessage');
const account = JSON.parse(localStorage.getItem('greenQuestAccount') || 'null');
const savedPoints = Number(localStorage.getItem('studentPoints') || 0);
const completedMissions = JSON.parse(localStorage.getItem('completedMissions') || '[]');

if (account) {
  document.getElementById('profileHeading').textContent = account.name;
  document.getElementById('profileAvatar').textContent = account.name.split(' ').map(function (word) {
    return word[0];
  }).join('').slice(0, 2).toUpperCase();
  document.getElementById('profile-name').value = account.name;
  document.getElementById('profile-email').value = account.email;
  document.getElementById('profile-class').value = account.studentClass;
  document.getElementById('profile-city').value = account.city;
}

// Points aur completed mission count saved progress ke according dikhata hai.
document.getElementById('profilePoints').textContent = savedPoints;
document.getElementById('profileProgressText').textContent = `${savedPoints} / 1,000 points to next level`;
const profileProgress = Math.min(savedPoints / 10, 100);
document.querySelector('.profile-summary .progress-bar span').style.width = `${profileProgress}%`;
document.querySelector('.profile-summary .progress-bar').setAttribute('aria-label', `${profileProgress} percent progress`);
document.getElementById('profileMissionCount').textContent = completedMissions.length;

profileForm.addEventListener('submit', function (event) {
  event.preventDefault();
  const updatedAccount = {
    name: document.getElementById('profile-name').value.trim(),
    email: document.getElementById('profile-email').value.trim().toLowerCase(),
    password: account ? account.password : '',
    studentClass: document.getElementById('profile-class').value,
    city: document.getElementById('profile-city').value
  };

  localStorage.setItem('greenQuestAccount', JSON.stringify(updatedAccount));
  document.getElementById('profileHeading').textContent = updatedAccount.name;
  profileMessage.textContent = 'Your profile changes have been saved.';
});
