from src.models.champion import Champion
from src.logic.battle.battle import Battle
from src.factories.champion_factory import create_champion
from src.common.report_generator import generate_report

def printChamp(champ: Champion):
    print(f"\nWe have champion \"{champ.getName()}\":")
    print(f"\tHP:{champ.getCurrHealth()}, ATK:{champ.getStat('ATK')}, DEF:{champ.getStat('DEF')},")
    print(f"\tSPATK:{champ.getStat('SPATK')}, SPDEF:{champ.getStat('SPDEF')}, SPD:{champ.getStat('SPD')}")
    mtype,mcount = champ.getMinion()
    print(f"\n\tMinion-Type: {mtype}, \n\tMinion-Count:{mcount}\n")

if __name__ == "__main__":
    Garen = create_champion("Garen")
    Darius = create_champion("Darius")
    
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
    
    