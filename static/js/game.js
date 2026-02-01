let battleHistory = [];
let leftMaxHp = 100;
let rightMaxHp = 100;
let currentIndex = 0;
let isPlaying = false;
let animationSpeed = 1000;

async function loadChampions() {
    try {
        const res = await fetch('/champions');
        const champions = await res.json();

        const leftSelect = document.getElementById('left-select');
        const rightSelect = document.getElementById('right-select');

        champions.forEach(c => {
            const opt1 = document.createElement('option');
            opt1.value = c.id;
            opt1.innerText = c.name;
            leftSelect.appendChild(opt1);

            const opt2 = document.createElement('option');
            opt2.value = c.id;
            opt2.innerText = c.name;
            rightSelect.appendChild(opt2);
        });

        // Set defaults
        if (champions.length > 0) leftSelect.value = champions[0].id;
        if (champions.length > 1) rightSelect.value = champions[1].id;

    } catch (e) {
        console.error("Failed to load champions", e);
    }
}

async function startBattle() {
    const btn = document.getElementById('start-btn');
    const status = document.getElementById('status-msg');
    const arena = document.getElementById('arena');
    const logs = document.getElementById('logs');
    const winnerBanner = document.getElementById('winner-banner');

    const leftId = document.getElementById('left-select').value;
    const rightId = document.getElementById('right-select').value;

    btn.disabled = true;
    status.innerText = "Simulating Battle...";
    logs.innerHTML = "";
    winnerBanner.style.display = 'none';

    try {
        const response = await fetch('/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ left_id: leftId, right_id: rightId })
        });
        const data = await response.json();

        if (data.detail) {
            alert("Error: " + data.detail);
            btn.disabled = false;
            return;
        }

        // Setup Init State
        // The server response format might be slightly different now.
        // WebBattle.run_to_end() returns { winner: str, logs: [...] }
        // Wait! We also need initial stats (HP) to render the bars correctly *before* the first log.
        // But the logs contain everything we need if the first log is Turn 1.
        // ...Actually, typical battle logs start with Turn 1, but we need Max HP for the bar.

        // Let's check src/api/server.py run_to_end return value again.
        // It returns {"winner": ..., "logs": ...}
        // It DOES NOT return max_hp info. We need to fix that in server.py or infer it.
        // Inferring is risky. Let's fix server.py in the next step.
        // For now, let's assume we will fix server.py to return initial state.

        // Assuming data structure: { winner: "...", logs: [...], left: {name, max_hp}, right: {name, max_hp} }

        document.getElementById('left-name').innerText = data.left.name;
        document.getElementById('right-name').innerText = data.right.name;

        leftMaxHp = data.left.max_hp;
        rightMaxHp = data.right.max_hp;

        updateHp('left', leftMaxHp, leftMaxHp);
        updateHp('right', rightMaxHp, rightMaxHp);

        battleHistory = data.logs;
        currentIndex = 0;

        arena.style.display = 'flex';
        status.innerText = "Battle Start!";

        // Start playback
        playBattle(data.winner);

    } catch (err) {
        console.error(err);
        status.innerText = "Failed to connect to server.";
        btn.disabled = false;
    }
}

// Init
loadChampions();

function updateHp(side, current, max) {
    const percent = Math.max(0, (current / max) * 100);
    document.getElementById(`${side}-hp-bar`).style.width = percent + '%';
    document.getElementById(`${side}-hp-text`).innerText = `${Math.ceil(current)} / ${max}`;
}

async function playBattle(winnerName) {
    isPlaying = true;

    for (const turn of battleHistory) {
        if (!isPlaying) break;

        await new Promise(r => setTimeout(r, animationSpeed));

        renderTurn(turn);
    }

    if (isPlaying) {
        await new Promise(r => setTimeout(r, 500));
        document.getElementById('winner-name').innerText = winnerName;
        document.getElementById('winner-banner').style.display = 'block';
        document.getElementById('status-msg').innerText = "Game Over";
        document.getElementById('start-btn').disabled = false;
        isPlaying = false;
    }
}

function renderTurn(turn) {
    const actorSide = (turn.actor === document.getElementById('left-name').innerText) ? 'left' : 'right';
    const targetSide = (actorSide === 'left') ? 'right' : 'left';

    // Highlight Actor
    const actorCard = document.getElementById(`${actorSide}-card`);
    const targetCard = document.getElementById(`${targetSide}-card`);

    actorCard.classList.add('active');
    setTimeout(() => actorCard.classList.remove('active'), 500);

    // Update Logs
    const logBox = document.getElementById('logs');
    const entry = document.createElement('div');
    entry.className = 'log-entry highlight';
    entry.innerHTML = `[Turn ${turn.turn}] <b>${turn.actor}</b> used ${turn.action}!`;
    if (turn.damage > 0) entry.innerHTML += ` Dealt <b>${turn.damage}</b> damage.`;
    logBox.prepend(entry);

    // Apply Damage / Update HP
    if (turn.damage > 0) {
        setTimeout(() => {
            targetCard.classList.add('hit');
            showDamage(targetCard, turn.damage);
            setTimeout(() => targetCard.classList.remove('hit'), 300);

            // Note: History contains HP *after* the turn
            // We need to be careful with left/right mapping from the server vs client
            // The history object has 'left_hp' and 'right_hp' which correspond to the server's view
            // assuming left and right don't swap, we can use them directly.

            // Server 'left' is always the first player (P1), 'right' is P2.
            updateHp('left', turn.left_hp, leftMaxHp);
            updateHp('right', turn.right_hp, rightMaxHp);

        }, 300);
    } else {
        // Just update HP in case of healing or other changes
        updateHp('left', turn.left_hp, leftMaxHp);
        updateHp('right', turn.right_hp, rightMaxHp);
    }
}

function showDamage(element, amount) {
    const pop = document.createElement('div');
    pop.className = 'damage-pop';
    pop.innerText = `-${amount}`;
    pop.style.left = '50%';
    pop.style.top = '30%';
    element.appendChild(pop);
    setTimeout(() => pop.remove(), 1000);
}
