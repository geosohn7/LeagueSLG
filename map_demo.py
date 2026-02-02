import time
from datetime import datetime, timedelta
from src.models.world_map import WorldMap
from src.logic.map_manager import MapManager
from src.models.march import MarchStatus
from src.factories.champion_factory import create_champion
from src.models.building import BuildingType
from src.models.tile import TileCategory, ResourceType

def run_occupation_demo():
    print("=== LeagueSLG 실전 점령 및 후퇴 시스템 데모 ===")
    
    # 1. 월드 맵 및 매니저 초기화 (10x10)
    world_map = WorldMap(width=10, height=10)
    map_mgr = MapManager(world_map)
    user_id = "Player1"
    
    # 2. 내 부대 준비 (가렌 Lv.1)
    # 이제 병력은 챔피언의 HP와 동일합니다.
    garen_obj = create_champion("Garen")
    garen_obj.level = 1
    garen_obj.recalculate_stats()
    garen_obj.reset_status() # HP 풀회복
    
    garen_army = map_mgr.create_army(user_id, garen_obj)
    
    # 3. 본진 및 홈 좌표 설정
    main_castle_pos = (1, 1)
    map_mgr.world_map.place_building(BuildingType.MAIN_CASTLE, user_id, main_castle_pos)
    garen_army.set_position(1, 1) # 주성 위치에서 시작
    garen_army.home_pos = (1, 1)  # 패배 시 돌아올 곳
    
    print(f"\n[초기화 완료] {garen_army}")
    world_map.display_ascii()

    # 강제로 (5, 5)를 고레벨 토지로 변경하여 '패배 및 후퇴' 시나리오 테스트
    test_tile = world_map.get_tile(5, 5)
    test_tile.category = TileCategory.RESOURCE
    test_tile.res_type = ResourceType.IRON
    test_tile.level = 10
    target_pos = (5, 5)

    print(f"\n[공격 개시] {target_pos} (Lv.{world_map.get_tile(target_pos[0], target_pos[1]).level}) 토지로 행군!")
    march = map_mgr.send_march(garen_army, target_pos)

    # 4. 시뮬레이션 루프
    start_time = time.time()
    if march:
        march.arrival_time = datetime.now() + timedelta(seconds=2)
    
    running = True
    while running and (time.time() - start_time < 20):
        map_mgr.update()
        
        # 데모 가속: 후퇴 중인 부대가 있다면 시간을 당김
        for m in map_mgr.active_marches:
            if m.status == MarchStatus.RETURNING and m.arrival_time > datetime.now() + timedelta(seconds=2):
                m.arrival_time = datetime.now() + timedelta(seconds=2)
                # print("(데모 가속: 후퇴 부대 2초 뒤 본진 도착 예정)")
                
        if not map_mgr.active_marches:
            if garen_army.status == "STATIONED":
                print("\n>>> 점령 성공 후 주둔 중. 데모를 종료합니다.")
                running = False
            elif garen_army.status == "IDLE":
                print("\n>>> 본진 복귀 완료. 데모를 종료합니다.")
                running = False
        
        time.sleep(0.5)

    # 5. 최종 시각화
    from src.common.map_visualizer import visualize_map
    import webbrowser
    import os
    
    report_path = visualize_map(world_map, "reports/world_map.html", user_id)
    print(f"\n최종 월드 맵 리포트: {report_path}")
    webbrowser.open(f"file:///{report_path}")

if __name__ == "__main__":
    run_occupation_demo()
