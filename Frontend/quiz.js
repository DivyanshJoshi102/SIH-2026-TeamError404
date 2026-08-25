const quizForm = document.getElementById('quizForm');
const quizSetup = document.getElementById('quizSetup');
const quizPanel = document.getElementById('quizPanel');
const quizResult = document.getElementById('quizResult');
const classSelect = document.getElementById('quiz-class');
const topicSelect = document.getElementById('quiz-topic');
const questionTitle = document.getElementById('questionTitle');
const quizLabel = document.getElementById('quizLabel');
const quizProgress = document.getElementById('quizProgress');
const quizProgressBar = document.getElementById('quizProgressBar');
const quizQuestion = document.getElementById('quizQuestion');
const quizOptions = document.getElementById('quizOptions');
const quizFeedback = document.getElementById('quizFeedback');
const nextQuestion = document.getElementById('nextQuestion');
const account = JSON.parse(localStorage.getItem('greenQuestAccount') || 'null');

const sampleQuestions = {
  climate: [
    { question: 'Which source produces electricity without burning fuel?', options: ['Coal', 'Solar energy', 'Diesel', 'Petrol'], answer: 'Solar energy', explanation: 'Solar panels use sunlight to produce electricity.' },
    { question: 'Which action saves the most energy at home?', options: ['Leaving lights on', 'Using LED bulbs', 'Opening the fridge often', 'Running empty fans'], answer: 'Using LED bulbs', explanation: 'LED bulbs use less electricity than traditional bulbs.' },
    { question: 'What gas is a major cause of global warming?', options: ['Oxygen', 'Nitrogen', 'Carbon dioxide', 'Helium'], answer: 'Carbon dioxide', explanation: 'Carbon dioxide traps heat in the atmosphere.' }
  ],
  waste: [
    { question: 'Which bin is best for fruit and vegetable peels?', options: ['Compost bin', 'E-waste bin', 'Glass bin', 'Metal bin'], answer: 'Compost bin', explanation: 'Organic waste can break down into useful compost.' },
    { question: 'What does recycling do?', options: ['Creates more waste', 'Turns used items into new materials', 'Uses more plastic', 'Wastes water'], answer: 'Turns used items into new materials', explanation: 'Recycling keeps useful materials out of landfills.' },
    { question: 'Which is a reusable item?', options: ['Plastic straw', 'Paper receipt', 'Steel water bottle', 'Snack wrapper'], answer: 'Steel water bottle', explanation: 'A steel bottle can be used many times.' }
  ],
  water: [
    { question: 'Which habit helps save water while brushing?', options: ['Keep the tap running', 'Turn off the tap', 'Use a hose', 'Fill the sink twice'], answer: 'Turn off the tap', explanation: 'Turning off the tap prevents clean water from being wasted.' },
    { question: 'What is rainwater harvesting?', options: ['Collecting rain for use', 'Removing rain clouds', 'Wasting rainwater', 'Heating rainwater'], answer: 'Collecting rain for use', explanation: 'Rainwater can be collected and stored for later use.' },
    { question: 'Which leak should be fixed quickly?', options: ['A dripping tap', 'A dry bucket', 'A closed bottle', 'An empty glass'], answer: 'A dripping tap', explanation: 'A small leak can waste a large amount of water over time.' }
  ],
  biodiversity: [
    { question: 'What is biodiversity?', options: ['One type of plant', 'Variety of living things', 'Only wild animals', 'A type of weather'], answer: 'Variety of living things', explanation: 'Biodiversity means the variety of plants, animals and other life.' },
    { question: 'Which action protects local wildlife?', options: ['Planting native trees', 'Destroying nests', 'Throwing waste', 'Removing ponds'], answer: 'Planting native trees', explanation: 'Native trees provide food and shelter for local species.' },
    { question: 'Why are bees important?', options: ['They pollinate plants', 'They create plastic', 'They waste water', 'They remove oxygen'], answer: 'They pollinate plants', explanation: 'Pollination helps many plants produce fruits and seeds.' }
  ]
};

let questions = [];
let currentQuestion = 0;
let score = 0;

if (account && account.studentClass) {
  classSelect.value = account.studentClass;
}

quizForm.addEventListener('submit', function (event) {
  event.preventDefault();
  questions = sampleQuestions[topicSelect.value];
  currentQuestion = 0;
  score = 0;
  quizSetup.hidden = true;
  quizResult.hidden = true;
  quizPanel.hidden = false;
  quizLabel.textContent = `${classSelect.value} | ${topicSelect.options[topicSelect.selectedIndex].text}`;
  showQuestion();
});

function showQuestion() {
  const item = questions[currentQuestion];
  questionTitle.textContent = `Question ${currentQuestion + 1}`;
  quizProgress.textContent = `${currentQuestion + 1} / ${questions.length}`;
  quizProgressBar.style.width = `${(currentQuestion / questions.length) * 100}%`;
  quizQuestion.textContent = item.question;
  quizOptions.innerHTML = '';
  quizFeedback.textContent = '';
  nextQuestion.hidden = true;

  item.options.forEach(function (option) {
    const button = document.createElement('button');
    button.className = 'quiz-option';
    button.type = 'button';
    button.textContent = option;
    button.addEventListener('click', function () {
      checkAnswer(button, option, item);
    });
    quizOptions.appendChild(button);
  });
}

function checkAnswer(selectedButton, selectedOption, item) {
  const optionButtons = quizOptions.querySelectorAll('button');
  optionButtons.forEach(function (button) {
    button.disabled = true;
    if (button.textContent === item.answer) button.classList.add('correct-answer');
  });

  if (selectedOption === item.answer) {
    score += 1;
    quizFeedback.textContent = `Correct! ${item.explanation}`;
    selectedButton.classList.add('correct-answer');
  } else {
    quizFeedback.textContent = `Not quite. ${item.explanation}`;
    selectedButton.classList.add('wrong-answer');
  }

  nextQuestion.hidden = false;
}

nextQuestion.addEventListener('click', function () {
  currentQuestion += 1;
  if (currentQuestion < questions.length) {
    showQuestion();
  } else {
    showResult();
  }
});

function showResult() {
  quizPanel.hidden = true;
  quizResult.hidden = false;
  document.getElementById('resultTitle').textContent = `${score} / ${questions.length} correct`;
  document.getElementById('resultText').textContent = score === questions.length
    ? 'Excellent work. You mastered this topic.'
    : 'Good attempt. Review the explanations and try again.';
}

document.getElementById('restartQuiz').addEventListener('click', function () {
  quizResult.hidden = true;
  quizSetup.hidden = false;
});
