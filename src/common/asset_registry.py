"""
에셋 레지스트리 관리 모듈
게임 내 모든 비주얼 에셋(3D 모델, 이미지, 애니메이션)의 경로를 관리합니다.
"""
import json
import os
from typing import Dict, Optional, Any


class AssetRegistry:
    """에셋 레지스트리 관리 클래스"""
    
    def __init__(self, registry_path: str = "data/assets_registry.json"):
        """
        Args:
            registry_path: 에셋 레지스트리 JSON 파일 경로
        """
        self.registry_path = registry_path
        self.registry: Dict[str, Any] = {}
        self._load_registry()
    
    def _load_registry(self):
        """레지스트리 파일 로드"""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            print(f"Warning: Asset registry not found at {self.registry_path}")
            self.registry = {}
    
    def get_champion_assets(self, champion_key: str) -> Optional[Dict[str, Any]]:
        """
        챔피언의 에셋 정보 조회
        
        Args:
            champion_key: 챔피언 키 (예: "Garen")
            
        Returns:
            에셋 정보 딕셔너리 또는 None
        """
        champions = self.registry.get("champions", {})
        return champions.get(champion_key)
    
    def get_building_assets(self, building_type: str, level: int = 1) -> Optional[Dict[str, Any]]:
        """
        건물의 에셋 정보 조회
        
        Args:
            building_type: 건물 타입 (예: "MAIN_CASTLE")
            level: 건물 레벨
            
        Returns:
            에셋 정보 딕셔너리 (레벨에 맞게 경로 치환됨)
        """
        buildings = self.registry.get("buildings", {})
        building_data = buildings.get(building_type)
        
        if building_data:
            # 레벨에 따라 경로 치환
            assets = building_data.get("assets", {}).copy()
            for key, path in assets.items():
                if isinstance(path, str) and "{level}" in path:
                    assets[key] = path.format(level=level)
            
            return {
                **building_data,
                "assets": assets
            }
        
        return None
    
    def get_tile_assets(self, resource_type: str, level: int = 1) -> Optional[Dict[str, Any]]:
        """
        타일의 에셋 정보 조회
        
        Args:
            resource_type: 자원 타입 (예: "FOOD", "WOOD")
            level: 타일 레벨
            
        Returns:
            에셋 정보 딕셔너리 (레벨에 맞게 경로 치환됨)
        """
        tiles = self.registry.get("tiles", {})
        tile_data = tiles.get(resource_type)
        
        if tile_data:
            # 레벨에 따라 경로 치환
            assets = tile_data.get("assets", {}).copy()
            for key, path in assets.items():
                if isinstance(path, str) and "{level}" in path:
                    assets[key] = path.format(level=level)
            
            return {
                **tile_data,
                "assets": assets
            }
        
        return None
    
    def get_effect_assets(self, effect_name: str) -> Optional[Dict[str, Any]]:
        """
        이펙트의 에셋 정보 조회
        
        Args:
            effect_name: 이펙트 이름 (예: "damage_hit")
            
        Returns:
            이펙트 에셋 정보
        """
        effects = self.registry.get("effects", {})
        return effects.get(effect_name)
    
    def get_ui_assets(self, category: str, name: str) -> Optional[str]:
        """
        UI 에셋 경로 조회
        
        Args:
            category: UI 카테고리 (예: "backgrounds", "buttons")
            name: 에셋 이름
            
        Returns:
            에셋 경로 문자열
        """
        ui = self.registry.get("ui", {})
        category_assets = ui.get(category, {})
        return category_assets.get(name)
    
    def get_fallback_color(self, entity_type: str, entity_key: str) -> str:
        """
        에셋이 없을 때 사용할 대체 색상 조회
        
        Args:
            entity_type: 엔티티 타입 ("champions", "buildings", "tiles")
            entity_key: 엔티티 키
            
        Returns:
            색상 코드 (예: "#4169E1")
        """
        entities = self.registry.get(entity_type, {})
        entity_data = entities.get(entity_key, {})
        fallback = entity_data.get("fallback", {})
        return fallback.get("color", "#FFFFFF")
    
    def asset_exists(self, asset_path: str, base_dir: str = "assets") -> bool:
        """
        에셋 파일이 실제로 존재하는지 확인
        
        Args:
            asset_path: 에셋 상대 경로
            base_dir: 기본 디렉토리
            
        Returns:
            파일 존재 여부
        """
        full_path = os.path.join(base_dir, asset_path)
        return os.path.exists(full_path)


# 전역 에셋 레지스트리 인스턴스
_asset_registry: Optional[AssetRegistry] = None


def get_asset_registry() -> AssetRegistry:
    """전역 에셋 레지스트리 인스턴스 반환"""
    global _asset_registry
    if _asset_registry is None:
        _asset_registry = AssetRegistry()
    return _asset_registry
