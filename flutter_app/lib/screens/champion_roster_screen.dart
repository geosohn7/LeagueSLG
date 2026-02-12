import 'package:flutter/material.dart';
import '../models/champion_model.dart';
import '../services/champion_service.dart';
import '../widgets/animated_champion_card.dart';
import '../utils/page_transitions.dart';
import 'champion_detail_screen.dart';

class ChampionRosterScreen extends StatefulWidget {
  final String userId;

  const ChampionRosterScreen({super.key, required this.userId});

  @override
  State<ChampionRosterScreen> createState() => _ChampionRosterScreenState();
}

class _ChampionRosterScreenState extends State<ChampionRosterScreen> {
  final ChampionService _championService = ChampionService();
  List<Champion> _champions = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadChampions();
  }

  Future<void> _loadChampions() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final champions = await _championService.getChampionRoster(widget.userId);
      setState(() {
        _champions = champions;
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('보유 장수'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(_errorMessage!),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadChampions,
                    child: const Text('다시 시도'),
                  ),
                ],
              ),
            )
          : _champions.isEmpty
          ? const Center(
              child: Text(
                '보유한 장수가 없습니다',
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),
            )
          : Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.deepPurple.shade50, Colors.white],
                ),
              ),
              child: GridView.builder(
                padding: const EdgeInsets.all(16),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  childAspectRatio: 0.7,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                ),
                itemCount: _champions.length,
                itemBuilder: (context, index) {
                  final champion = _champions[index];
                  return AnimatedChampionCard(
                    name: champion.name,
                    level: champion.level,
                    faction: champion.faction,
                    factionColor: _getFactionColor(champion.faction),
                    index: index,
                    onTap: () {
                      Navigator.push(
                        context,
                        HeroPageRoute(
                          builder: (context) => ChampionDetailScreen(
                            userId: widget.userId,
                            championId: champion.id,
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
    );
  }
}

class ChampionCard extends StatelessWidget {
  final Champion champion;
  final Color factionColor;
  final VoidCallback onTap;

  const ChampionCard({
    super.key,
    required this.champion,
    required this.factionColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              factionColor.withOpacity(0.8),
              factionColor.withOpacity(0.6),
            ],
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Stack(
            children: [
              // 배경 패턴
              Positioned.fill(
                child: Container(
                  decoration: BoxDecoration(
                    gradient: RadialGradient(
                      center: Alignment.topRight,
                      radius: 1.5,
                      colors: [
                        Colors.white.withOpacity(0.2),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),

              // 콘텐츠
              Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 레벨 배지
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        'Lv.${champion.level}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),

                    const Spacer(),

                    // 장수 초상화 (플레이스홀더)
                    Center(
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.3),
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                        ),
                        child: const Icon(
                          Icons.person,
                          size: 50,
                          color: Colors.white,
                        ),
                      ),
                    ),

                    const Spacer(),

                    // 장수 이름
                    Center(
                      child: Text(
                        champion.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          shadows: [Shadow(color: Colors.black, blurRadius: 4)],
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),

                    const SizedBox(height: 4),

                    // 진영
                    Center(
                      child: Text(
                        champion.faction,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 12,
                          shadows: const [
                            Shadow(color: Colors.black, blurRadius: 2),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
