import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'battle_screen.dart';
import 'start_screen.dart';
import 'city_management_screen.dart';

void main() {
  runApp(const LeagueSLGApp());
}

class LeagueSLGApp extends StatelessWidget {
  const LeagueSLGApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LeagueSLG',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const StartScreen(),
    );
  }
}

class MapScreen extends StatefulWidget {
  final String userId;
  const MapScreen({super.key, required this.userId});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  // API 설정
  static const String apiBaseUrl = 'http://localhost:8000';

  // 맵 데이터
  int mapWidth = 0;
  int mapHeight = 0;
  List<TileData> tiles = [];

  // 로딩 상태
  bool isLoading = true;
  String? errorMessage;

  // 선택된 타일
  TileData? selectedTile;

  // 타이머
  Timer? updateTimer;

  // 맵 조작 컨트롤러
  final TransformationController _transformationController =
      TransformationController();
  bool _isMapCentered = false;

  @override
  void initState() {
    super.initState();
    loadMapData(isInitial: true);

    // 1초마다 게임 상태 업데이트 (화면 깜빡임 없이 백그라운드에서 진행)
    updateTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      updateGameState();
      checkBattleResults();
    });
  }

  @override
  void dispose() {
    updateTimer?.cancel();
    _transformationController.dispose();
    super.dispose();
  }

  /// 맵 데이터 로드
  Future<void> loadMapData({bool isInitial = false}) async {
    try {
      if (isInitial) {
        setState(() {
          isLoading = true;
          errorMessage = null;
        });
      }

      final response = await http.get(Uri.parse('$apiBaseUrl/map'));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        setState(() {
          mapWidth = data['width'];
          mapHeight = data['height'];
          tiles = (data['tiles'] as List)
              .map((tile) => TileData.fromJson(tile))
              .toList();
          isLoading = false;
        });

        // 처음 로드 시에만 내 성 위치로 이동
        if (isInitial && !_isMapCentered) {
          _centerMapOnCastle();
        }
      } else {
        if (isInitial) {
          setState(() {
            errorMessage = 'Failed to load map: ${response.statusCode}';
            isLoading = false;
          });
        }
      }
    } catch (e) {
      if (isInitial) {
        setState(() {
          errorMessage = 'Error: $e';
          isLoading = false;
        });
      }
    }
  }

  /// 내 성 위치로 맵 중심 이동
  void _centerMapOnCastle() {
    if (mapWidth == 0 || tiles.isEmpty) return;

    // 내 성 찾기
    TileData? castleTile;
    try {
      castleTile = tiles.firstWhere(
        (t) => t.ownerId == widget.userId && t.buildingType == 'MAIN_CASTLE',
      );
    } catch (e) {
      // 내 성이 없으면 (0,0) 혹은 내 영토 중 하나
      try {
        castleTile = tiles.firstWhere((t) => t.ownerId == widget.userId);
      } catch (e) {
        // 내 영토도 없으면 패스
      }
    }

    // 중심 좌표 계산
    double targetX = 0;
    double targetY = 0;

    if (castleTile != null) {
      targetX = castleTile.x * 40.0; // 40 is tileSize
      targetY = castleTile.y * 40.0;
    } else {
      // 중앙
      targetX = (mapWidth * 40.0) / 2;
      targetY = (mapHeight * 40.0) / 2;
    }

    // 뷰포트 중앙에 오도록 오프셋 조정 (화면 크기를 정확히 알기 어려우므로 대략적 보정)
    // Zoom 레벨 1.0 기준
    final x = -targetX + 200; // 200 is arbitrary screen half width
    final y = -targetY + 300;

    _transformationController.value = Matrix4.identity()
      ..translate(x, y)
      ..scale(1.5); // 약간 줌인

    _isMapCentered = true;
  }

  /// 게임 상태 업데이트
  Future<void> updateGameState() async {
    try {
      // 서버에 상태 업데이트 요청
      await http.post(Uri.parse('$apiBaseUrl/map/update'));

      // 화면 깜빡임 없이 데이터만 갱신
      await loadMapData(isInitial: false);
    } catch (e) {
      debugPrint('Update Error: $e');
    }
  }

  /// 전투 결과 폴링
  Future<void> checkBattleResults() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/battle/results/${widget.userId}'),
      );

      if (response.statusCode == 200) {
        final List<dynamic> results = json.decode(response.body);

        if (results.isNotEmpty) {
          // 첫 번째 전투 결과만 표시 (순차 처리)
          // 여러 개일 경우 큐 처리 로직이 더 필요할 수 있음
          final battleData = results.first['result'];

          if (mounted) {
            // 타이머 일시 정지 (팝업 중 중복 실행 방지)
            updateTimer?.cancel();

            await Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => BattleScreen(battleData: battleData),
              ),
            );

            // 복귀 후 타이머 재개
            updateTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
              updateGameState();
              checkBattleResults();
            });
          }
        }
      }
    } catch (e) {
      debugPrint('Battle Check Error: $e');
    }
  }

  /// 타일 클릭 핸들러
  void onTileClicked(TileData tile) {
    setState(() {
      selectedTile = tile;
    });
  }

  // 행군 보내기
  Future<void> sendMarch(int targetX, int targetY) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/map/march'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': widget.userId,
          'champion_key': 'Garen', // Default champion for now
          'target_x': targetX,
          'target_y': targetY,
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('March started!')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to march: ${response.body}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text('LeagueSLG - ${widget.userId}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.apartment),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      CityManagementScreen(userId: widget.userId),
                ),
              );
            },
            tooltip: 'City Management',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: loadMapData,
            tooltip: 'Reload Map',
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : errorMessage != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(errorMessage!),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: loadMapData,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : Row(
              children: [
                // 맵 영역
                Expanded(
                  flex: 3,
                  child: InteractiveViewer(
                    transformationController: _transformationController,
                    boundaryMargin: const EdgeInsets.all(500), // 넉넉하게
                    minScale: 0.1,
                    maxScale: 4.0,
                    child: Center(
                      child: MapGrid(
                        width: mapWidth,
                        height: mapHeight,
                        tiles: tiles,
                        onTileClicked: onTileClicked,
                        selectedTile: selectedTile,
                      ),
                    ),
                  ),
                ),
                // 사이드바 (타일 정보)
                Container(
                  width: 300,
                  color: Colors.grey[200],
                  child: selectedTile != null
                      ? TileInfoPanel(
                          tile: selectedTile!,
                          currentUserId: widget.userId,
                          onMarch: (x, y) => sendMarch(x, y),
                        )
                      : const Center(
                          child: Text('Select a tile to view details'),
                        ),
                ),
              ],
            ),
    );
  }
}

/// 맵 그리드 위젯
class MapGrid extends StatelessWidget {
  final int width;
  final int height;
  final List<TileData> tiles;
  final Function(TileData) onTileClicked;
  final TileData? selectedTile;

  const MapGrid({
    super.key,
    required this.width,
    required this.height,
    required this.tiles,
    required this.onTileClicked,
    this.selectedTile,
  });

  @override
  Widget build(BuildContext context) {
    const double tileSize = 40.0;

    return SizedBox(
      width: width * tileSize,
      height: height * tileSize,
      child: GridView.builder(
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: width,
          childAspectRatio: 1.0,
        ),
        itemCount: tiles.length,
        itemBuilder: (context, index) {
          final tile = tiles[index];
          final isSelected =
              selectedTile?.x == tile.x && selectedTile?.y == tile.y;

          return GestureDetector(
            onTap: () => onTileClicked(tile),
            child: TileWidget(tile: tile, isSelected: isSelected),
          );
        },
      ),
    );
  }
}

/// 개별 타일 위젯
class TileWidget extends StatelessWidget {
  final TileData tile;
  final bool isSelected;

  const TileWidget({super.key, required this.tile, required this.isSelected});

  Color getTileColor() {
    if (tile.category == 'OBSTACLE') {
      return Colors.grey[700]!;
    } else if (tile.category == 'RESOURCE') {
      switch (tile.resourceType) {
        case 'FOOD':
          return Colors.green[400]!;
        case 'WOOD':
          return Colors.brown[400]!;
        case 'IRON':
          return Colors.grey[500]!;
        case 'STONE':
          return Colors.blue[300]!;
        default:
          return Colors.white;
      }
    } else if (tile.category == 'BUILDING') {
      return Colors.purple[300]!;
    }
    return Colors.white;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: getTileColor(),
        border: Border.all(
          color: isSelected ? Colors.yellow : Colors.black26,
          width: isSelected ? 3.0 : 0.5,
        ),
      ),
      child: Stack(
        children: [
          // 건물 아이콘
          if (tile.category == 'BUILDING' && tile.buildingType != null)
            Center(
              child: Text(
                tile.buildingType == 'MAIN_CASTLE' ? '🏰' : '🏠',
                style: const TextStyle(fontSize: 20),
              ),
            ),

          // 레벨 표시
          if (tile.level > 1)
            Positioned(
              top: 2,
              left: 2,
              child: Container(
                padding: const EdgeInsets.all(2),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'Lv${tile.level}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 8,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          // 소유주 표시
          if (tile.ownerId != null)
            Positioned(
              bottom: 2,
              right: 2,
              child: Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: Colors.blue, // TODO: Color based on owner
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 1),
                ),
              ),
            ),

          // 부대 표시
          if (tile.hasArmy)
            Positioned(
              bottom: 2,
              left: 2,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 2),
                decoration: BoxDecoration(
                  color: Colors.redAccent,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text('⚔️', style: TextStyle(fontSize: 10)),
              ),
            ),
        ],
      ),
    );
  }
}

/// 타일 정보 패널
class TileInfoPanel extends StatelessWidget {
  final TileData tile;
  final String currentUserId;
  final Function(int, int) onMarch;

  const TileInfoPanel({
    super.key,
    required this.tile,
    required this.currentUserId,
    required this.onMarch,
  });

  @override
  Widget build(BuildContext context) {
    bool isMyTile = tile.ownerId == currentUserId;
    bool canAttack = !isMyTile && tile.category != 'OBSTACLE';

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Tile (${tile.x}, ${tile.y})',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          _buildInfoRow('Category', tile.category),
          if (tile.resourceType != null)
            _buildInfoRow('Resource', tile.resourceType!),
          _buildInfoRow('Level', tile.level.toString()),
          if (tile.ownerId != null)
            _buildInfoRow('Owner', tile.ownerId!)
          else
            _buildInfoRow('Owner', 'Neutral'),

          if (tile.buildingType != null)
            _buildInfoRow('Building', tile.buildingType!),

          const SizedBox(height: 24),

          if (canAttack)
            ElevatedButton.icon(
              onPressed: () => onMarch(tile.x, tile.y),
              icon: const Icon(Icons.flag),
              label: const Text('March Here'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                foregroundColor: Colors.white,
              ),
            ),

          if (isMyTile)
            const Text(
              'My Territory',
              style: TextStyle(
                color: Colors.green,
                fontWeight: FontWeight.bold,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

/// 타일 데이터 모델
class TileData {
  final int x;
  final int y;
  final String category;
  final int level;
  final String? ownerId;
  final String? resourceType;
  final String? buildingType;
  final bool hasArmy;

  TileData({
    required this.x,
    required this.y,
    required this.category,
    required this.level,
    this.ownerId,
    this.resourceType,
    this.buildingType,
    this.hasArmy = false,
  });

  factory TileData.fromJson(Map<String, dynamic> json) {
    String? bType;
    if (json['building'] != null) {
      bType = json['building']['type'];
    }

    return TileData(
      x: json['x'],
      y: json['y'],
      category: json['category'],
      level: json['level'],
      ownerId: json['owner_id'],
      resourceType: json['resource_type'],
      buildingType: bType,
      hasArmy: json['army'] != null,
    );
  }
}
