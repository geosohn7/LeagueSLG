// 장수 모델 클래스
class Champion {
  final int id;
  final String key;
  final String name;
  final int level;
  final int exp;
  final String faction;
  final Map<String, dynamic> images;
  final int rating;

  Champion({
    required this.id,
    required this.key,
    required this.name,
    required this.level,
    required this.exp,
    required this.faction,
    required this.images,
    required this.rating,
  });

  factory Champion.fromJson(Map<String, dynamic> json) {
    return Champion(
      id: json['id'] ?? 0,
      key: json['key'] ?? '',
      name: json['name'] ?? '',
      level: json['level'] ?? 1,
      exp: json['exp'] ?? 0,
      faction: json['faction'] ?? 'Unknown',
      images: json['images'] ?? {},
      rating: json['rating'] ?? 0,
    );
  }
}

// 장수 상세 정보 모델
class ChampionDetail {
  final int id;
  final String name;
  final int level;
  final int exp;
  final String faction;
  final Map<String, dynamic> stats;
  final List<int> baseStat;
  final List<double> statGrowth;
  final int maxHp;
  final int currentHp;
  final String description;
  final Map<String, dynamic> images;
  final List<Map<String, dynamic>> items;
  final List<Map<String, dynamic>> bonds;
  final List<Map<String, dynamic>> skills;

  ChampionDetail({
    required this.id,
    required this.name,
    required this.level,
    required this.exp,
    required this.faction,
    required this.stats,
    required this.baseStat,
    required this.statGrowth,
    required this.maxHp,
    required this.currentHp,
    required this.description,
    required this.images,
    required this.items,
    required this.bonds,
    required this.skills,
  });

  factory ChampionDetail.fromJson(Map<String, dynamic> json) {
    return ChampionDetail(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      level: json['level'] ?? 1,
      exp: json['exp'] ?? 0,
      faction: json['faction'] ?? 'Unknown',
      stats: json['stats'] ?? {},
      baseStat: List<int>.from(json['base_stat'] ?? []),
      statGrowth: List<double>.from(json['stat_growth'] ?? []),
      maxHp: json['max_hp'] ?? 0,
      currentHp: json['current_hp'] ?? 0,
      description: json['description'] ?? '',
      images: json['images'] ?? {},
      items: List<Map<String, dynamic>>.from(json['items'] ?? []),
      bonds: List<Map<String, dynamic>>.from(json['bonds'] ?? []),
      skills: List<Map<String, dynamic>>.from(json['skills'] ?? []),
    );
  }
}
