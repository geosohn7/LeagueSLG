import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// 에셋 레지스트리 관리 클래스
/// 게임 내 모든 비주얼 에셋의 경로를 관리하고 로드합니다.
class AssetRegistry {
  static AssetRegistry? _instance;
  Map<String, dynamic> _registry = {};
  bool _isLoaded = false;

  AssetRegistry._();

  /// 싱글톤 인스턴스 반환
  static AssetRegistry get instance {
    _instance ??= AssetRegistry._();
    return _instance!;
  }

  /// 레지스트리 초기화 (앱 시작 시 호출)
  Future<void> initialize() async {
    if (_isLoaded) return;

    try {
      // 백엔드에서 에셋 레지스트리를 가져올 수도 있지만,
      // 현재는 로컬에 복사본을 두는 방식으로 구현
      // final String jsonString = await rootBundle.loadString('assets/assets_registry.json');
      // _registry = json.decode(jsonString);

      // 임시로 빈 레지스트리로 시작
      _registry = {};
      _isLoaded = true;

      debugPrint('Asset Registry initialized');
    } catch (e) {
      debugPrint('Failed to load asset registry: $e');
      _registry = {};
    }
  }

  /// 챔피언 에셋 정보 조회
  ChampionAssets? getChampionAssets(String championKey) {
    final champions = _registry['champions'] as Map<String, dynamic>?;
    if (champions == null) return null;

    final championData = champions[championKey] as Map<String, dynamic>?;
    if (championData == null) return null;

    return ChampionAssets.fromJson(championData);
  }

  /// 건물 에셋 정보 조회
  BuildingAssets? getBuildingAssets(String buildingType, int level) {
    final buildings = _registry['buildings'] as Map<String, dynamic>?;
    if (buildings == null) return null;

    final buildingData = buildings[buildingType] as Map<String, dynamic>?;
    if (buildingData == null) return null;

    return BuildingAssets.fromJson(buildingData, level);
  }

  /// 타일 에셋 정보 조회
  TileAssets? getTileAssets(String resourceType, int level) {
    final tiles = _registry['tiles'] as Map<String, dynamic>?;
    if (tiles == null) return null;

    final tileData = tiles[resourceType] as Map<String, dynamic>?;
    if (tileData == null) return null;

    return TileAssets.fromJson(tileData, level);
  }

  /// Fallback 색상 조회
  Color getFallbackColor(String entityType, String entityKey) {
    final entities = _registry[entityType] as Map<String, dynamic>?;
    if (entities == null) return Colors.grey;

    final entityData = entities[entityKey] as Map<String, dynamic>?;
    if (entityData == null) return Colors.grey;

    final fallback = entityData['fallback'] as Map<String, dynamic>?;
    if (fallback == null) return Colors.grey;

    final colorString = fallback['color'] as String?;
    if (colorString == null) return Colors.grey;

    return _parseColor(colorString);
  }

  Color _parseColor(String hexColor) {
    final hex = hexColor.replaceAll('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }
}

/// 챔피언 에셋 정보
class ChampionAssets {
  final String id;
  final String name;
  final String? model3d;
  final String? texture;
  final String? icon;
  final String? portrait;
  final Map<String, String> animations;
  final Color fallbackColor;
  final String fallbackText;

  ChampionAssets({
    required this.id,
    required this.name,
    this.model3d,
    this.texture,
    this.icon,
    this.portrait,
    this.animations = const {},
    required this.fallbackColor,
    required this.fallbackText,
  });

  factory ChampionAssets.fromJson(Map<String, dynamic> json) {
    final assets = json['assets'] as Map<String, dynamic>?;
    final fallback = json['fallback'] as Map<String, dynamic>?;
    final animations = assets?['animations'] as Map<String, dynamic>?;

    return ChampionAssets(
      id: json['id'] as String,
      name: json['name'] as String,
      model3d: assets?['model_3d'] as String?,
      texture: assets?['texture'] as String?,
      icon: assets?['icon'] as String?,
      portrait: assets?['portrait'] as String?,
      animations: animations?.map((k, v) => MapEntry(k, v as String)) ?? {},
      fallbackColor: _parseColor(fallback?['color'] as String? ?? '#FFFFFF'),
      fallbackText: fallback?['icon_text'] as String? ?? '?',
    );
  }

  static Color _parseColor(String hexColor) {
    final hex = hexColor.replaceAll('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }
}

/// 건물 에셋 정보
class BuildingAssets {
  final String id;
  final String name;
  final String? model3d;
  final String? texture;
  final String? icon;
  final Color fallbackColor;

  BuildingAssets({
    required this.id,
    required this.name,
    this.model3d,
    this.texture,
    this.icon,
    required this.fallbackColor,
  });

  factory BuildingAssets.fromJson(Map<String, dynamic> json, int level) {
    final assets = json['assets'] as Map<String, dynamic>?;
    final fallback = json['fallback'] as Map<String, dynamic>?;

    // 레벨에 따라 경로 치환
    String? model3d = assets?['model_3d'] as String?;
    if (model3d != null && model3d.contains('{level}')) {
      model3d = model3d.replaceAll('{level}', level.toString());
    }

    return BuildingAssets(
      id: json['id'] as String,
      name: json['name'] as String,
      model3d: model3d,
      texture: assets?['texture'] as String?,
      icon: assets?['icon'] as String?,
      fallbackColor: _parseColor(fallback?['color'] as String? ?? '#FFFFFF'),
    );
  }

  static Color _parseColor(String hexColor) {
    final hex = hexColor.replaceAll('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }
}

/// 타일 에셋 정보
class TileAssets {
  final String id;
  final String name;
  final String? model3d;
  final String? texture;
  final String? icon;
  final Color fallbackColor;

  TileAssets({
    required this.id,
    required this.name,
    this.model3d,
    this.texture,
    this.icon,
    required this.fallbackColor,
  });

  factory TileAssets.fromJson(Map<String, dynamic> json, int level) {
    final assets = json['assets'] as Map<String, dynamic>?;
    final fallback = json['fallback'] as Map<String, dynamic>?;

    // 레벨에 따라 경로 치환
    String? model3d = assets?['model_3d'] as String?;
    if (model3d != null && model3d.contains('{level}')) {
      model3d = model3d.replaceAll('{level}', level.toString());
    }

    return TileAssets(
      id: json['id'] as String,
      name: json['name'] as String,
      model3d: model3d,
      texture: assets?['texture'] as String?,
      icon: assets?['icon'] as String?,
      fallbackColor: _parseColor(fallback?['color'] as String? ?? '#FFFFFF'),
    );
  }

  static Color _parseColor(String hexColor) {
    final hex = hexColor.replaceAll('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }
}
