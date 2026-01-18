from classes.champion import Champion
from utils.stats import Stats

def printChamp(champ: Champion):
    print(f"\nWe have champion \"{champ.getName()}\":")
    print(f"\tHP:{champ.getCurrHealth()}, ATK:{champ.getStat('ATK')}, DEF:{champ.getStat('DEF')},")
    print(f"\tSPATK:{champ.getStat('SPATK')}, SPDEF:{champ.getStat('SPDEF')}, SPD:{champ.getStat('SPD')}")
    mtype,mcount = champ.getMinion()
    print(f"\n\tMinion-Type: {mtype}, \n\tMinion-Count:{mcount}\n")

if __name__ == "__main__":
    Garen = Champion(
        'Garen', 
        [690, 69, 38, 0, 32, 340], 
        [0, 0, 0, 0, 0, 0], 
        1, 
        ('Meele', 10)
    )
    printChamp(Garen)

    print(f"Test 1: Garen Takes 100 Damage\n\tremaining health = {Garen._take_damage(100.0)}")
    printChamp(Garen)
    
    