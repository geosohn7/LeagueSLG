from src.models.champion import Champion
from src.logic.battle.battle import Battle
from src.factories.champion_factory import create_champion
from src.common.report_generator import generate_report
from src.models.user import User
from src.common.database import DatabaseManager
import webbrowser
import os

def printChamp(champ: Champion):
    print(f"\nWe have champion \"{champ.getName()}\":")
    print(f"\tHP:{champ.getCurrHealth()}, ATK:{champ.getStat('ATK')}, DEF:{champ.getStat('DEF')},")
    print(f"\tSPATK:{champ.getStat('SPATK')}, SPDEF:{champ.getStat('SPDEF')}, SPD:{champ.getStat('SPD')}")
    mtype,mcount = champ.getMinion()
    print(f"\n\tMinion-Type: {mtype}, \n\tMinion-Count:{mcount}\n")

if __name__ == "__main__":
    # 데이터베이스 및 유저 초기화
    db_manager = DatabaseManager()
    user = User("Geo", db_manager)

    # 챔피언이 없으면 기본 지급
    if not user.champions:
        print("--- 신규 유저 환영: 챔피언 지급 ---")
        user.add_champion("Garen")
        user.add_champion("Darius")

    # 유저의 챔피언 가져오기
    # 단순화를 위해 이름으로 검색 (실제로는 ID 등을 사용할 수 있음)
    Garen = next((c for c in user.champions if c.name == "Garen"), None)
    Darius = next((c for c in user.champions if c.name == "Darius"), None)

    if not Garen or not Darius:
        print("오류: 필요한 챔피언을 찾을 수 없습니다.")
        exit(1)
    
    # 아이템 장착 테스트
    print("--- 아이템 장착 ---")
    Garen.equip_item("LongSword")
    Garen.equip_item("ChainVest")
    Darius.equip_item("SwiftBoots")
    
    printChamp(Garen)
    printChamp(Darius)

    print("\n--- 전투 시작 ---")
    battle1 = Battle(Garen, Darius)
    battle1.start()

    # 웹 리포트 생성
    generate_report(battle1, "reports/battle_report.html")
    print("\n전투 시각화 리포트(reports/battle_report.html)가 생성되었습니다.")
    
    # 리포트 자동 열기
    report_abs_path = os.path.abspath("reports/battle_report.html")
    webbrowser.open(f"file:///{report_abs_path}")
    print("브라우저에서 리포트를 열었습니다.")

    # 전투 결과 저장
    user.save_data()
    print("\n--- 데이터 저장 완료 ---")