from classes.champion import Champion
from utils.stats import Stats

def printChamp(champ: Champion):
    print(f"\nWe have chapion \"{champ.getName()}\":")
    print(f"\tATK:{champ.getStat('ATK')}, DEF:{champ.getStat('DEF')},")
    print(f"\tSPATK:{champ.getStat('SPATK')}, SPDEF:{champ.getStat('SPDEF')}, SPD:{champ.getStat('SPD')}")
    mtype,mcount = champ.getMinion()
    print(f"\n\tMinion-Type: {mtype}, \n\tMinion-Count:{mcount}\n")

if __name__ == "__main__":
    Garen = Champion('Garen', [69, 38, 0, 32, 340], ('Meele', 10))
    printChamp(Garen)
    