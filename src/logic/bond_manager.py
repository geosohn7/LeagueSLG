
from typing import List, Dict, Any
from data.bond_loader import load_bonds

class BondManager:
    """
    Manages relationship (Bond/Inyeon) logic for armies.
    """
    def __init__(self):
        # Load bonds data from JSON
        self.bonds = load_bonds()

    def get_active_bonds(self, champion_names: List[str]) -> List[Dict[str, Any]]:
        """
        Given a list of champion names in an army/unit, returns list of active bonds data.
        
        Logic Rules:
        1. If bond requires EXACTLY 2 people -> Both must be present.
        2. If bond definition has 3 OR MORE people -> At least 3 must be present to activate.
           (Maximum army size is usually 3, so this effectively means '3 of them'.)
        """
        active_bonds = []
        champion_set = set(champion_names) # Determine presence efficiently
        
        for bond_id, bond_data in self.bonds.items():
            required_members = set(bond_data.get("required", []))
            required_count = len(required_members)
            
            if not required_members:
                continue

            # Calculate how many required members are actually in the army
            present_members = required_members.intersection(champion_set)
            present_count = len(present_members)

            is_active = False

            if required_count == 2:
                # Rule 1: For pairs, BOTH must be present (2 out of 2)
                if present_count == 2:
                    is_active = True
            elif required_count >= 3:
                # Rule 2: For groups of 3+, AT LEAST 3 must be present
                if present_count >= 3:
                    is_active = True
            
            if is_active:
                bond_info = bond_data.copy()
                bond_info['id'] = bond_id
                # Optionally mark which members triggered it
                bond_info['active_members'] = list(present_members)
                active_bonds.append(bond_info)
                
        return active_bonds

    def calculate_total_buffs(self, active_bonds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregates buffs from a list of active bonds.
        Returns a flat list of buff objects to be applied by the Battle System.
        """
        total_buffs = []
        for bond in active_bonds:
            if "buffs" in bond:
                total_buffs.extend(bond["buffs"])
        return total_buffs

    def get_related_bonds(self, champion_name: str) -> List[Dict[str, Any]]:
        """
        특정 장수가 포함된 모든 인연을 반환합니다.
        
        Args:
            champion_name: 장수 이름 (예: "계백")
            
        Returns:
            해당 장수가 포함된 인연 목록 (bond_id, name, description, required, buffs 포함)
        """
        related_bonds = []
        
        for bond_id, bond_data in self.bonds.items():
            required_members = bond_data.get("required", [])
            
            # 이 장수가 인연 목록에 포함되어 있는지 확인
            if champion_name in required_members:
                bond_info = bond_data.copy()
                bond_info['id'] = bond_id
                related_bonds.append(bond_info)
        
        return related_bonds
