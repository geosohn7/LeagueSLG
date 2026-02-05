import os

MAP_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>LeagueSLG 월드 맵</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
        
        :root {{
            --bg-dark: #050a14;
            --tile-border: rgba(120, 90, 40, 0.2);
            --gold: #c8aa6e;
            --food: #27ae60;
            --wood: #a04000;
            --iron: #7f8c8d;
            --stone: #2471a3;
            --obstacle: #1a1a1a;
            --owned: rgba(30, 200, 100, 0.3);
        }}

        body {{
            background-color: var(--bg-dark);
            color: #f0e6d2;
            font-family: 'Outfit', sans-serif;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .map-container {{
            display: grid;
            grid-template-columns: repeat({width}, 45px);
            grid-template-rows: repeat({height}, 45px);
            gap: 2px;
            background: #111;
            border: 3px solid var(--gold);
            padding: 5px;
            border-radius: 4px;
        }}

        .tile {{
            width: 45px;
            height: 45px;
            background: #222;
            border: 1px solid var(--tile-border);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.1s;
        }}

        .tile:hover {{ transform: scale(1.1); z-index: 10; border-color: var(--gold); }}

        /* 카테고리별 스타일 */
        .category-RESOURCE {{ opacity: 0.8; }}
        .category-OBSTACLE {{ background: var(--obstacle); color: #444; }}
        .category-BUILDING {{ background: rgba(200, 170, 110, 0.2); }}

        /* 자원 종류별 테두리 */
        .res-FOOD {{ border-bottom: 3px solid var(--food); }}
        .res-WOOD {{ border-bottom: 3px solid var(--wood); }}
        .res-IRON {{ border-bottom: 3px solid var(--iron); }}
        .res-STONE {{ border-bottom: 3px solid var(--stone); }}

        .level-badge {{
            position: absolute;
            top: 2px;
            right: 2px;
            font-size: 9px;
            color: var(--gold);
        }}

        .army-mark {{
            background: #f1c40f;
            color: #000;
            font-size: 8px;
            font-weight: bold;
            padding: 1px 3px;
            border-radius: 2px;
            position: absolute;
            bottom: 2px;
            left: 2px;
        }}

        .building-icon {{ font-size: 20px; }}
        .obstacle-icon {{ font-size: 18px; filter: grayscale(1); }}
        
        .owned-overlay {{
            position: absolute;
            width: 100%;
            height: 100%;
            background: var(--owned);
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <h1>Strategic World Map</h1>
    <div class="map-container">
        {tiles_html}
    </div>
    <div style="margin-top: 20px; display: flex; gap: 15px;">
        <span>🌾 농지</span> <span>🌲 목재</span> <span>⚒️ 철광</span> <span>💎 석재</span> <span>⛰️ 장애물</span>
    </div>
</body>
</html>
"""

def visualize_map(world_map, output_path="reports/world_map.html", my_id="Player1"):
    tiles_html = ""
    res_icons = {"FOOD": "🌾", "WOOD": "🌲", "IRON": "⚒️", "STONE": "💎"}
    
    for y in range(world_map.height):
        for x in range(world_map.width):
            tile = world_map.get_tile(x, y)
            classes = [f"tile", f"category-{tile.category.name}", f"res-{tile.res_type.name}"]
            
            content = f'<div class="level-badge">L{tile.level}</div>'
            
            if tile.category == tile.category.OBSTACLE:
                content += '<div class="obstacle-icon">⛰️</div>'
            elif tile.building:
                if tile.is_building_root:
                    icon = "🏰" if tile.building.type.name == "MAIN_CASTLE" else "🏠"
                    content += f'<div class="building-icon">{icon}</div>'
            elif tile.category == tile.category.RESOURCE:
                icon = res_icons.get(tile.res_type.name, "")
                content += f'<div style="font-size:16px">{icon}</div>'

            if tile.owner_id == my_id:
                content += '<div class="owned-overlay"></div>'
            
            if tile.occupying_army:
                content += f'<div class="army-mark">{tile.occupying_army.champion.name[0]} {tile.occupying_army.troop_count}</div>'
            
            title = f"({x},{y}) {tile.category.value}"
            if tile.res_type.name != "NONE": title += f" - {tile.res_type.value} Lv.{tile.level}"
            if tile.owner_id: title += f" (소유: {tile.owner_id})"

            tiles_html += f'<div class="{" ".join(classes)}" title="{title}">{content}</div>'

    html = MAP_HTML_TEMPLATE.format(width=world_map.width, height=world_map.height, tiles_html=tiles_html)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(output_path)
