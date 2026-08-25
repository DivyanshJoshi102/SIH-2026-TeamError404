// Signup form se student data lekar browser ke localStorage me demo account save karta hai.
const signupForm = document.getElementById('signupForm');
const loginForm = document.getElementById('loginForm');

if (signupForm) {
  signupForm.addEventListener('submit', function (event) {
    event.preventDefault();

    const account = {
      name: document.getElementById('signup-name').value.trim(),
      email: document.getElementById('signup-email').value.trim().toLowerCase(),
      password: document.getElementById('signup-password').value,
      studentClass: document.getElementById('signup-class').value,
      city: document.getElementById('signup-city').value
    };

    const existingAccount = JSON.parse(localStorage.getItem('greenQuestAccount') || 'null');

    // Sirf same email par duplicate account banne se rokta hai.
    if (existingAccount && existingAccount.email === account.email) {
      document.getElementById('signupMessage').textContent = 'An account already exists. Please log in.';
      return;
    }

    // Demo ke liye data save ho raha hai; real project me secure backend use karna hoga.
    localStorage.setItem('greenQuestAccount', JSON.stringify(account));
    document.getElementById('signupMessage').textContent = 'Account created! Opening your dashboard...';
    window.location.href = 'dashboard.html';
  });
}

if (loginForm) {
  loginForm.addEventListener('submit', function (event) {
    event.preventDefault();

    const account = JSON.parse(localStorage.getItem('greenQuestAccount'));
    const email = document.getElementById('login-email').value.trim().toLowerCase();
    const password = document.getElementById('login-password').value;
    const loginMessage = document.getElementById('loginMessage');

    // Saved account ke email aur password ko entered values se compare karta hai.
    if (!account || account.email !== email || account.password !== password) {
      loginMessage.textContent = 'Email or password is incorrect.';
      return;
    }

    loginMessage.textContent = 'Login successful! Opening your dashboard...';
    window.location.href = 'dashboard.html';
  });
}
