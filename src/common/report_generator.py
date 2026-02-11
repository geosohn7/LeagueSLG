import json
import os

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>전투 리포트 - LeagueSLG</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
        
        :root {{
            --bg-color: #010a13;
            --card-bg: #091428;
            --border-color: #785a28;
            --gold: #c8aa6e;
            --health: #1e6432;
            --damage: #c83232;
        }}

        body {{
            background-color: var(--bg-color);
            color: #f0e6d2;
            font-family: 'Noto+Sans+KR', sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}

        header {{
            margin-top: 40px;
            text-align: center;
        }}

        h1 {{
            color: var(--gold);
            text-shadow: 0 0 10px rgba(200, 170, 110, 0.5);
            letter-spacing: 2px;
        }}

        .battle-arena {{
            display: flex;
            justify-content: space-between;
            width: 95%;
            max-width: 1200px;
            margin-top: 50px;
            gap: 40px;
        }}

        .team-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            width: 45%;
        }}

        .team-title {{
            text-align: center;
            font-size: 1.5em;
            color: var(--gold);
            margin-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }}

        .champion-card {{
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            gap: 15px;
            position: relative;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .champion-card.active {{
            border-color: #f0e6d2;
            box-shadow: 0 0 20px rgba(240, 230, 210, 0.5);
            transform: scale(1.02);
            z-index: 10;
        }}

        .champion-image {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 2px solid var(--gold);
            object-fit: cover;
            background-color: #000;
        }}

        .champion-info {{
            flex-grow: 1;
        }}

        .champion-name {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .hp-bar-container {{
            background: #222;
            height: 15px;
            width: 100%;
            border: 1px solid #444;
            overflow: hidden;
            border-radius: 2px;
        }}

        .hp-bar {{
            height: 100%;
            background: linear-gradient(to right, #28a745, #1e6432);
            width: 100%;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .hp-text {{
            font-size: 12px;
            margin-top: 3px;
            text-align: right;
            color: #aaa;
        }}

        .log-container {{
            margin-top: 50px;
            width: 90%;
            max-width: 800px;
            background: rgba(9, 20, 40, 0.8);
            border: 1px solid var(--border-color);
            height: 250px;
            overflow-y: auto;
            padding: 15px;
            border-radius: 4px;
        }}

        .log-entry {{
            padding: 8px;
            border-bottom: 1px solid rgba(120, 90, 40, 0.2);
            animation: slideIn 0.3s ease-out;
            font-size: 0.9em;
        }}

        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-10px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}

        .controls {{
            margin-top: 20px;
            display: flex;
            gap: 15px;
        }}

        button {{
            background: var(--gold);
            border: none;
            padding: 10px 25px;
            color: #010a13;
            font-weight: bold;
            cursor: pointer;
            border-radius: 2px;
            text-transform: uppercase;
        }}

        button:hover {{
            background: #e1c382;
        }}

        .damage-pop {{
            position: absolute;
            right: 20px;
            top: 10px;
            color: var(--damage);
            font-weight: bold;
            font-size: 20px;
            animation: fadeUp 1.0s forwards;
            pointer-events: none;
            text-shadow: 1px 1px 2px black;
        }}

        .dead {{
             filter: grayscale(100%) brightness(0.5);
             border-color: #444;
        }}

        @keyframes fadeUp {{
            0% {{ opacity: 0; transform: translateY(0); }}
            20% {{ opacity: 1; }}
            100% {{ opacity: 0; transform: translateY(-30px); }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>전투 연대기</h1>
        <p id="battle-title"></p>
    </header>

    <div class="battle-arena">
        <!-- Left Team -->
        <div class="team-container">
            <div class="team-title" id="left-team-name">Team A</div>
            <div id="left-team-cards"></div>
        </div>

        <!-- Right Team -->
        <div class="team-container">
            <div class="team-title" id="right-team-name">Team B</div>
            <div id="right-team-cards"></div>
        </div>
    </div>

    <div class="controls">
        <button onclick="playNext()">다음 턴</button>
        <button onclick="autoPlay()">자동 재생</button>
    </div>

    <div id="logs" class="log-container"></div>

    <script>
        const history = {history_json};
        
        // Arrays of champion data
        const leftData = {left_data_json};  // [ {{name, max_hp, images}}, ... ]
        const rightData = {right_data_json}; // [ {{name, max_hp, images}}, ... ]

        const leftTeamName = "{left_name}";
        const rightTeamName = "{right_name}";

        document.getElementById('left-team-name').innerText = leftTeamName;
        document.getElementById('right-team-name').innerText = rightTeamName;
        document.getElementById('battle-title').innerText = `${{leftTeamName}} VS ${{rightTeamName}}`;

        // Function to create cards
        function renderCards(containerId, teamData, side) {{
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            teamData.forEach((champ, index) => {{
                const card = document.createElement('div');
                card.id = `${{side}}-card-${{index}}`;
                card.className = 'champion-card';
                card.innerHTML = `
                    <div style="position: relative;">
                        <img id="${{side}}-img-${{index}}" src="../${{champ.images.default}}" class="champion-image">
                    </div>
                    <div class="champion-info">
                        <div class="champion-name">${{champ.name}}</div>
                        <div class="hp-bar-container">
                            <div id="${{side}}-hp-bar-${{index}}" class="hp-bar" style="width: 100%;"></div>
                        </div>
                        <div id="${{side}}-hp-text-${{index}}" class="hp-text">${{champ.max_hp}} / ${{champ.max_hp}}</div>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        // Initialize UI
        renderCards('left-team-cards', leftData, 'left');
        renderCards('right-team-cards', rightData, 'right');

        let currentIndex = 0;
        let isAutoPlaying = false;
        let animationTimeout = null;

        function updateUI(step) {{
            // 1. Clean up previous active states
            document.querySelectorAll('.champion-card').forEach(c => c.classList.remove('active'));
            // Reset images to default (if animation was interrupted)
            if (animationTimeout) clearTimeout(animationTimeout);
            
            // Reset all images to default just in case
            leftData.forEach((c, i) => document.getElementById(`left-img-${{i}}`).src = "../" + c.images.default);
            rightData.forEach((c, i) => document.getElementById(`right-img-${{i}}`).src = "../" + c.images.default);

            // 2. Identify Actor & Target
            const actorSide = step.actor_team;
            const actorIndex = step.actor_index;
            const targetSide = step.target_team;
            const targetIndex = step.target_index;

            const actorCardId = `${{actorSide}}-card-${{actorIndex}}`;
            const targetCardId = `${{targetSide}}-card-${{targetIndex}}`;
            
            const actorImgId = `${{actorSide}}-img-${{actorIndex}}`;
            const targetImgId = `${{targetSide}}-img-${{targetIndex}}`;

            const actorImages = (actorSide === 'left' ? leftData : rightData)[actorIndex].images;
            const targetImages = (targetSide === 'left' ? leftData : rightData)[targetIndex].images;

            // 3. Animation
            const actorCard = document.getElementById(actorCardId);
            if (actorCard) {{
                actorCard.classList.add('active');
                document.getElementById(actorImgId).src = "../" + actorImages.attack;
            }}

            const targetCard = document.getElementById(targetCardId);
            if (targetCard && step.damage > 0) {{
                document.getElementById(targetImgId).src = "../" + targetImages.hit;
                showDamage(targetCardId, step.damage);
            }}

            // 4. Reset images after delay
            animationTimeout = setTimeout(() => {{
                if (actorCard) document.getElementById(actorImgId).src = "../" + actorImages.default;
                if (targetCard) document.getElementById(targetImgId).src = "../" + targetImages.default;
            }}, 800);

            // 5. Update HP Bars
            // Left Team
            step.left_hp.forEach((hp, idx) => {{
                const maxHp = leftData[idx].max_hp;
                updateHpBar('left', idx, hp, maxHp);
            }});

            // Right Team
            step.right_hp.forEach((hp, idx) => {{
                const maxHp = rightData[idx].max_hp;
                updateHpBar('right', idx, hp, maxHp);
            }});

            // 6. Log
            const logBox = document.getElementById('logs');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<strong>[Turn ${{step.turn}}]</strong> ${{step.actor}}: ${{step.action}}! (${{step.damage}} 데미지)`;
            logBox.prepend(entry);
        }}

        function updateHpBar(side, index, currentHp, maxHp) {{
            const bar = document.getElementById(`${{side}}-hp-bar-${{index}}`);
            const text = document.getElementById(`${{side}}-hp-text-${{index}}`);
            const card = document.getElementById(`${{side}}-card-${{index}}`);

            if (!bar || !text) return;

            const percent = (currentHp / maxHp) * 100;
            bar.style.width = Math.max(0, percent) + '%';
            text.innerText = `${{Math.max(0, currentHp)}} / ${{maxHp}}`;

            if (currentHp <= 0) {{
                card.classList.add('dead');
            }} else {{
                card.classList.remove('dead');
            }}
        }}

        function showDamage(cardId, amount) {{
            const card = document.getElementById(cardId);
            if (!card) return;
            const pop = document.createElement('div');
            pop.className = 'damage-pop';
            pop.innerText = `-${{amount}}`;
            card.appendChild(pop);
            setTimeout(() => pop.remove(), 1000);
        }}

        function playNext() {{
            if (currentIndex < history.length) {{
                updateUI(history[currentIndex]);
                currentIndex++;
            }} else {{
                alert("전투가 종료되었습니다.");
                isAutoPlaying = false;
            }}
        }}

        function autoPlay() {{
            if (isAutoPlaying) return;
            isAutoPlaying = true;
            const interval = setInterval(() => {{
                if (currentIndex >= history.length || !isAutoPlaying) {{
                    clearInterval(interval);
                    isAutoPlaying = false;
                    return;
                }}
                playNext();
            }}, 1000); // 1.0s interval
        }}
    </script>
</body>
</html>
"""

def generate_report(battle_instance, output_path="battle_report.html"):
    # Prepare detailed team data
    left_data = []
    for champ in battle_instance.left_team:
        left_data.append({
            "name": champ.name,
            "max_hp": champ.max_hp,
            "images": champ.images
        })

    right_data = []
    for champ in battle_instance.right_team:
        right_data.append({
            "name": champ.name,
            "max_hp": champ.max_hp,
            "images": champ.images
        })
    
    report_html = HTML_TEMPLATE.format(
        history_json=json.dumps(battle_instance.history),
        left_data_json=json.dumps(left_data),
        right_data_json=json.dumps(right_data),
        left_name=f"Team {battle_instance.left_army.unit_type}",
        right_name=f"Team {battle_instance.right_army.unit_type}"
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_html)
    
    print(f"리포트 생성 완료: {os.path.abspath(output_path)}")
