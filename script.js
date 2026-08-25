// Button click hone par student ko ek simple confirmation message milta hai.
const missionButton = document.getElementById('missionButton');
const message = document.getElementById('message');

missionButton.addEventListener('click', function () {
  message.textContent = 'Your first mission is ready. Let us make an impact!';
  missionButton.textContent = 'Mission selected';
});
