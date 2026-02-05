import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'battle_screen.dart';

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
      home: const MapScreen(),
    );
  }
}

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

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

  @override
  void initState() {
    super.initState();
    loadMapData(isInitial: true);

    // 1초마다 게임 상태 업데이트 (화면 깜빡임 없이 백그라운드에서 진행)
    updateTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      updateGameState();
    });
  }

  @override
  void dispose() {
    updateTimer?.cancel();
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

  /// 게임 상태 업데이트
  Future<void> updateGameState() async {
    try {
      // 서버에 상태 업데이트 요청 (행군 처리 등)
      await http.post(Uri.parse('$apiBaseUrl/map/update'));

      // 화면 깜빡임 없이 데이터만 갱신
      await loadMapData(isInitial: false);
    } catch (e) {
      // 에러 발생 시 로그만 출력하거나 무시
      debugPrint('Update Error: $e');
    }
  }

  /// 타일 클릭 핸들러
  void onTileClicked(TileData tile) {
    setState(() {
      selectedTile = tile;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('LeagueSLG - World Map'),
        actions: [
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
                    boundaryMargin: const EdgeInsets.all(100),
                    minScale: 0.5,
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
                      ? TileInfoPanel(tile: selectedTile!)
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
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
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

  const TileInfoPanel({super.key, required this.tile});

  @override
  Widget build(BuildContext context) {
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
          const SizedBox(height: 24),
          if (tile.ownerId == null && tile.category == 'RESOURCE')
            ElevatedButton.icon(
              onPressed: () async {
                // 전투 시뮬레이션 실행
                try {
                  // 임시로 Garen vs Darius 전투 시뮬레이션
                  final response = await http.post(
                    Uri.parse('http://localhost:8000/simulate'),
                    headers: {'Content-Type': 'application/json'},
                    body: json.encode({
                      'left_id': 'Garen',
                      'right_id': 'Darius',
                    }),
                  );

                  if (response.statusCode == 200) {
                    final battleData = json.decode(response.body);

                    // 전투 화면으로 이동
                    if (context.mounted) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              BattleScreen(battleData: battleData),
                        ),
                      );
                    }
                  } else {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            'Failed to simulate battle: ${response.statusCode}',
                          ),
                        ),
                      );
                    }
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(
                      context,
                    ).showSnackBar(SnackBar(content: Text('Error: $e')));
                  }
                }
              },
              icon: const Icon(Icons.send),
              label: const Text('Send Army'),
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

  TileData({
    required this.x,
    required this.y,
    required this.category,
    required this.level,
    this.ownerId,
    this.resourceType,
  });

  factory TileData.fromJson(Map<String, dynamic> json) {
    return TileData(
      x: json['x'],
      y: json['y'],
      category: json['category'],
      level: json['level'],
      ownerId: json['owner_id'],
      resourceType: json['resource_type'],
    );
  }
}
