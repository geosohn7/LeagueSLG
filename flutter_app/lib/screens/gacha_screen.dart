import 'package:flutter/material.dart';
import '../services/gacha_service.dart';

class GachaScreen extends StatefulWidget {
  final String userId;

  const GachaScreen({super.key, required this.userId});

  @override
  State<GachaScreen> createState() => _GachaScreenState();
}

class _GachaScreenState extends State<GachaScreen> {
  final GachaService _service = GachaService();
  Map<String, dynamic>? _config;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    try {
      final config = await _service.getGachaConfig();
      setState(() {
        _config = config;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _pullGacha(
    String type,
    String title,
    int cost,
    String currency,
  ) async {
    // 확인 다이얼로그
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text('$cost $currency을 사용하여 소환하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('소환'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    // 소환 실행
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final result = await _service.pullGacha(widget.userId, type);
      Navigator.pop(context); // 로딩 닫기

      // 결과 표시
      _showResultDialog(result);
    } catch (e) {
      Navigator.pop(context); // 로딩 닫기
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('소환 실패: $e'), backgroundColor: Colors.red),
      );
    }
  }

  void _showResultDialog(Map<String, dynamic> data) {
    print("Result Data: $data"); // 디버깅용

    // server.py:
    // "result": { "name": ..., "image": ..., "faction": ..., "rating": ... }
    final result = data['result'];
    final name = result['name'];
    final faction = result['faction'] ?? 'Unknown';
    // final imagePath = result['image'] ... (Not used properly yet)

    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.amber.withOpacity(0.5),
                blurRadius: 20,
                spreadRadius: 5,
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                '🎉 소환 성공! 🎉',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber,
                ),
              ),
              const SizedBox(height: 24),

              // 챔피언 카드 느낌
              Container(
                width: 150,
                height: 200,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: _getFactionColors(faction),
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.person, size: 80, color: Colors.white),
                    const SizedBox(height: 16),
                    Text(
                      name,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      faction,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),
              Text(data['message'] ?? ''),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('확인'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<Color> _getFactionColors(String faction) {
    if (faction == 'Goguryeo')
      return [Colors.red.shade400, Colors.red.shade900];
    if (faction == 'Baekje')
      return [Colors.blue.shade400, Colors.blue.shade900];
    if (faction == 'Silla')
      return [Colors.amber.shade400, Colors.amber.shade900];
    return [Colors.grey.shade400, Colors.grey.shade900];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('장수 소환')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(child: Text('Error: $_error'))
          : _buildBody(),
    );
  }

  Widget _buildBody() {
    // config 예: {"silver_gacha": {...}, "gold_gacha": {...}}
    final keys = _config!.keys.toList();

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: keys.length,
      itemBuilder: (context, index) {
        final key = keys[index];
        final item = _config![key];
        return _buildGachaCard(key, item);
      },
    );
  }

  Widget _buildGachaCard(String type, Map<String, dynamic> item) {
    String title = item['name'] ?? type;
    int cost = item['cost'] ?? 0;
    String currency = item['currency'] ?? 'gold';
    String desc = item['description'] ?? '장수를 소환합니다.';

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 배너 이미지 (색상으로 대체)
          Container(
            height: 120,
            decoration: BoxDecoration(
              color: type.contains('gold')
                  ? Colors.amber.shade700
                  : Colors.blueGrey,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(16),
              ),
            ),
            alignment: Alignment.center,
            child: Icon(
              type.contains('gold') ? Icons.stars : Icons.catching_pokemon,
              size: 64,
              color: Colors.white,
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(desc, style: TextStyle(color: Colors.grey[600])),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '비용: $cost $currency',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.blueAccent,
                      ),
                    ),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: type.contains('gold')
                            ? Colors.amber
                            : Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                      onPressed: () => _pullGacha(type, title, cost, currency),
                      child: const Text('1회 소환'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
