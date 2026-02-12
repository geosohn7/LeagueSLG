import 'package:flutter/material.dart';
import '../models/champion_model.dart';
import '../services/champion_service.dart';
import '../widgets/stats_radar_chart.dart';

class ChampionDetailScreen extends StatefulWidget {
  final String userId;
  final int championId;

  const ChampionDetailScreen({
    super.key,
    required this.userId,
    required this.championId,
  });

  @override
  State<ChampionDetailScreen> createState() => _ChampionDetailScreenState();
}

class _ChampionDetailScreenState extends State<ChampionDetailScreen>
    with SingleTickerProviderStateMixin {
  final ChampionService _championService = ChampionService();
  ChampionDetail? _championDetail;
  bool _isLoading = true;
  String? _errorMessage;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadChampionDetail();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadChampionDetail() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final detail = await _championService.getChampionDetail(
        widget.userId,
        widget.championId,
      );
      setState(() {
        _championDetail = detail;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Color _getFactionColor(String faction) {
    switch (faction) {
      case 'Goguryeo':
        return Colors.red.shade700;
      case 'Baekje':
        return Colors.blue.shade700;
      case 'Silla':
        return Colors.amber.shade700;
      case 'Gaya':
        return Colors.green.shade700;
      default:
        return Colors.grey.shade700;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.deepPurple,
          foregroundColor: Colors.white,
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_errorMessage != null) {
      return Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.deepPurple,
          foregroundColor: Colors.white,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(_errorMessage!),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadChampionDetail,
                child: const Text('다시 시도'),
              ),
            ],
          ),
        ),
      );
    }

    final champion = _championDetail!;
    final factionColor = _getFactionColor(champion.faction);

    return Scaffold(
      body: Stack(
        children: [
          // 배경 이미지 (플레이스홀더)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    factionColor.withOpacity(0.7),
                    factionColor.withOpacity(0.3),
                    Colors.black.withOpacity(0.8),
                  ],
                ),
              ),
            ),
          ),

          // 콘텐츠
          SafeArea(
            child: Column(
              children: [
                // 헤더 (이름, 레벨)
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.arrow_back, color: Colors.white),
                        onPressed: () => Navigator.pop(context),
                      ),
                      const Spacer(),
                      Column(
                        children: [
                          Text(
                            champion.name,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              shadows: [
                                Shadow(color: Colors.black, blurRadius: 8),
                              ],
                            ),
                          ),
                          Text(
                            'Lv.${champion.level} | ${champion.faction}',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.9),
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                      const Spacer(),
                      const SizedBox(width: 48), // 균형 맞추기
                    ],
                  ),
                ),

                // 탭 바
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: TabBar(
                    controller: _tabController,
                    indicator: BoxDecoration(
                      color: factionColor.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    labelColor: Colors.white,
                    unselectedLabelColor: Colors.white.withOpacity(0.6),
                    tabs: const [
                      Tab(text: '능력치'),
                      Tab(text: '아이템'),
                      Tab(text: '인연/설명'),
                    ],
                  ),
                ),

                // 탭 뷰
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildStatsTab(champion),
                      _buildItemsTab(champion),
                      _buildBondsTab(champion),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsTab(ChampionDetail champion) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 레이더 차트
          Center(
            child: StatsRadarChart(
              stats: champion.stats,
              color: _getFactionColor(champion.faction),
            ),
          ),
          const SizedBox(height: 24),

          // HP 바
          _buildStatCard(
            '체력',
            '${champion.currentHp} / ${champion.maxHp}',
            champion.currentHp / champion.maxHp,
            Colors.red,
          ),
          const SizedBox(height: 12),

          // 주요 스탯
          _buildStatCard(
            '공격력 (ATK)',
            champion.stats['ATK']?.toString() ?? '0',
            null,
            Colors.orange,
          ),
          const SizedBox(height: 8),
          _buildStatCard(
            '방어력 (DEF)',
            champion.stats['DEF']?.toString() ?? '0',
            null,
            Colors.blue,
          ),
          const SizedBox(height: 8),
          _buildStatCard(
            '지력 (INT)',
            champion.stats['SPATK']?.toString() ?? '0',
            null,
            Colors.purple,
          ),
          const SizedBox(height: 8),
          _buildStatCard(
            '속도 (SPD)',
            champion.stats['SPD']?.toString() ?? '0',
            null,
            Colors.green,
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(
    String label,
    String value,
    double? progress,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.3), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                value,
                style: TextStyle(
                  color: color,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          if (progress != null) ...[
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.white.withOpacity(0.2),
                valueColor: AlwaysStoppedAnimation<Color>(color),
                minHeight: 8,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildItemsTab(ChampionDetail champion) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const Text(
            '장착 아이템',
            style: TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(3, (index) {
              final hasItem = index < champion.items.length;
              return Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: hasItem
                        ? Colors.amber
                        : Colors.white.withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: hasItem
                    ? Center(
                        child: Text(
                          champion.items[index]['name'] ?? '아이템',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      )
                    : const Center(
                        child: Icon(Icons.add, color: Colors.white54, size: 40),
                      ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _buildBondsTab(ChampionDetail champion) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 설명
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '장수 열전',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  champion.description,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 14,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // 인연
          const Text(
            '인연 관계',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          if (champion.bonds.isEmpty)
            Center(
              child: Text(
                '관련 인연이 없습니다',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 14,
                ),
              ),
            )
          else
            ...champion.bonds.map((bond) {
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.amber.withOpacity(0.5),
                    width: 1,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      bond['name'] ?? '',
                      style: const TextStyle(
                        color: Colors.amber,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      bond['description'] ?? '',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: (bond['required'] as List<dynamic>? ?? [])
                          .map(
                            (name) => Chip(
                              label: Text(
                                name.toString(),
                                style: const TextStyle(fontSize: 11),
                              ),
                              backgroundColor: Colors.white.withOpacity(0.2),
                              labelStyle: const TextStyle(color: Colors.white),
                            ),
                          )
                          .toList(),
                    ),
                  ],
                ),
              );
            }).toList(),
        ],
      ),
    );
  }
}
