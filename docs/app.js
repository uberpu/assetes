let board = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
let currentPlayer = 'X';
let gameActive = true;
let aiBrain = {}; // The current Q-table loaded via JSON

const cells = document.querySelectorAll('.cell');
const statusDisplay = document.querySelector('#status');
const brainSelect = document.querySelector('#brain-select');
const modal = document.getElementById("modal");
const modalBody = document.getElementById("modal-body");
const closeBtn = document.querySelector(".close-btn");

const winConditions = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Cols
    [0, 4, 8], [2, 4, 6]             // Diagonals
];

// Initialize Game
function init() {
    loadManifest();

    cells.forEach(cell => {
        cell.addEventListener('click', handleCellClick);
    });

    document.getElementById('reset-btn').addEventListener('click', resetGame);
    document.getElementById('logs-btn').addEventListener('click', () => loadMarkdown('training_log.md'));
    document.getElementById('docs-btn').addEventListener('click', () => loadMarkdown('q_learning_agent.md'));

    brainSelect.addEventListener('change', loadBrain);

    closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (event) => { if (event.target == modal) modal.style.display = "none"; };
}

async function loadManifest() {
    try {
        const response = await fetch('models/manifest.json');
        if (!response.ok) throw new Error('No manifest found (Initial Run)');
        const manifest = await response.json();

        brainSelect.innerHTML = '';
        const defaultOption = document.createElement('option');
        defaultOption.value = 'random';
        defaultOption.textContent = 'Untrained Agent (Random)';
        brainSelect.appendChild(defaultOption);

        manifest.forEach(item => {
            const option = document.createElement('option');
            option.value = `models/${item.filename}`;
            option.textContent = `${item.id} - ${item.states} States Learned (${item.date})`;
            brainSelect.appendChild(option);
        });

        if (manifest.length > 0) {
            brainSelect.value = `models/${manifest[0].filename}`; // Select latest
            loadBrain();
        }
    } catch (e) {
        brainSelect.innerHTML = '<option value="random">Untrained Agent (Random)</option>';
        aiBrain = {};
    }
}

async function loadBrain() {
    const file = brainSelect.value;
    if (file === 'random') {
        aiBrain = {};
        console.log("Loaded Random Brain");
        return;
    }

    try {
        const response = await fetch(file);
        aiBrain = await response.json();
        console.log(`Loaded Brain: ${file} with ${Object.keys(aiBrain).length} states`);
        resetGame(); // restart match with new brain
    } catch (e) {
        console.error("Failed to load brain", e);
        aiBrain = {};
    }
}

function handleCellClick(e) {
    const clickedCell = e.target;
    const cellIndex = parseInt(clickedCell.getAttribute('data-index'));

    if (board[cellIndex] !== ' ' || !gameActive || currentPlayer !== 'X') {
        return;
    }

    makeMove(cellIndex, 'X');

    if (gameActive) {
        setTimeout(aiMove, 300); // slight delay for feel
    }
}

function makeMove(index, player) {
    board[index] = player;
    cells[index].innerText = player;
    cells[index].classList.add(player.toLowerCase());

    checkResult(player);
    if (gameActive) {
        currentPlayer = player === 'X' ? 'O' : 'X';
        statusDisplay.innerText = currentPlayer === 'X' ? "Your turn! You are X." : "AI is thinking...";
    }
}

function aiMove() {
    const availableMoves = board.map((val, idx) => val === ' ' ? idx : null).filter(val => val !== null);
    if (availableMoves.length === 0 || !gameActive) return;

    let chosenMove;
    const stateStr = board.join('');

    // Exploit Q-Table if available
    if (Object.keys(aiBrain).length > 0 && aiBrain[stateStr]) {
        let maxQ = -Infinity;
        let bestMoves = [];
        const actions = aiBrain[stateStr];

        // Find best known moves
        availableMoves.forEach(move => {
            const qVal = actions[move] !== undefined ? actions[move] : 0;
            if (qVal > maxQ) {
                maxQ = qVal;
                bestMoves = [move];
            } else if (qVal === maxQ) {
                bestMoves.push(move);
            }
        });

        chosenMove = bestMoves[Math.floor(Math.random() * bestMoves.length)];
        console.log(`AI knows state: ${stateStr}, picking ${chosenMove} with Q: ${maxQ}`);
    } else {
        // Random fallback
        chosenMove = availableMoves[Math.floor(Math.random() * availableMoves.length)];
        console.log(`AI unknown state or random mode, randomly picking ${chosenMove}`);
    }

    makeMove(chosenMove, 'O');
}

function checkResult(player) {
    let roundWon = false;
    for (let i = 0; i <= 7; i++) {
        const winCondition = winConditions[i];
        let a = board[winCondition[0]];
        let b = board[winCondition[1]];
        let c = board[winCondition[2]];

        if (a === ' ' || b === ' ' || c === ' ') continue;
        if (a === b && b === c) {
            roundWon = true;
            break;
        }
    }

    if (roundWon) {
        statusDisplay.innerText = player === 'X' ? 'You won!' : 'AI won! The training is working!';
        statusDisplay.style.color = player === 'X' ? 'var(--primary-color)' : 'var(--secondary-color)';
        gameActive = false;
        return;
    }

    let roundDraw = !board.includes(' ');
    if (roundDraw) {
        statusDisplay.innerText = 'Game ended in a draw!';
        statusDisplay.style.color = '#fff';
        gameActive = false;
        return;
    }
}

function resetGame() {
    board = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
    gameActive = true;
    currentPlayer = 'X';
    statusDisplay.innerText = "Your turn! You are X.";
    statusDisplay.style.color = "var(--text-color)";
    cells.forEach(cell => {
        cell.innerText = '';
        cell.classList.remove('x', 'o');
    });
}

async function loadMarkdown(filename) {
    try {
        const response = await fetch(filename);
        if (!response.ok) throw new Error("File not found. It might not be generated yet.");
        const text = await response.text();
        modalBody.innerHTML = marked.parse(text);
        modal.style.display = "block";
    } catch (error) {
        modalBody.innerHTML = `<h3>Error</h3><p>${error.message}</p><p>Ensure you have run the Continuous AI pipeline in GitHub Actions at least once!</p>`;
        modal.style.display = "block";
    }
}

// Start
document.addEventListener('DOMContentLoaded', init);
