import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class CityManagementScreen extends StatefulWidget {
  final String userId;
  const CityManagementScreen({super.key, required this.userId});

  @override
  State<CityManagementScreen> createState() => _CityManagementScreenState();
}

class _CityManagementScreenState extends State<CityManagementScreen> {
  static const String apiBaseUrl = 'http://localhost:8000';

  bool isLoading = true;
  Map<String, dynamic> userData = {};
  List<dynamic> buildings = [];
  int maxTroops = 1000;
  int draftAmount = 10;

  Timer? refreshTimer;

  @override
  void initState() {
    super.initState();
    loadData();
    // 5초마다 자동 새로고침
    refreshTimer = Timer.periodic(
      const Duration(seconds: 5),
      (_) => loadData(),
    );
  }

  @override
  void dispose() {
    refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> loadData() async {
    try {
      // 유저 정보
      final userRes = await http.get(
        Uri.parse('$apiBaseUrl/user/${widget.userId}'),
      );
      // 건물 정보
      final buildingRes = await http.get(
        Uri.parse('$apiBaseUrl/building/list/${widget.userId}'),
      );

      if (userRes.statusCode == 200 && buildingRes.statusCode == 200) {
        setState(() {
          userData = json.decode(userRes.body);
          final buildingData = json.decode(buildingRes.body);
          buildings = buildingData['buildings'] ?? [];
          maxTroops = buildingData['max_troops'] ?? 1000;
          isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Load error: $e');
    }
  }

  Future<void> upgradeBuilding(String buildingType) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/building/upgrade'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': widget.userId,
          'building_type': buildingType,
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('$buildingType 업그레이드 시작!')));
        loadData();
      } else {
        final error = json.decode(response.body);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('실패: ${error['detail']}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('오류: $e')));
    }
  }

  Future<void> instantFinish(String buildingType) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/building/instant_finish'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': widget.userId,
          'building_type': buildingType,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(data['message'] ?? '즉시 완료!')));
        loadData();
      } else {
        final error = json.decode(response.body);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('실패: ${error['detail']}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('오류: $e')));
    }
  }

  Future<void> draftTroops() async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/troops/draft'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'user_id': widget.userId, 'amount': draftAmount}),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('$draftAmount명 징병 시작!')));
        loadData();
      } else {
        final error = json.decode(response.body);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('실패: ${error['detail']}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('오류: $e')));
    }
  }

  String getBuildingIcon(String type) {
    switch (type) {
      case 'Barracks':
        return '🏛️';
      case 'Farm':
        return '🌾';
      case 'Mine':
        return '⛏️';
      case 'Wall':
        return '🏰';
      case 'House':
        return '🏠';
      case 'Trading Post':
        return '💱';
      case 'Smithy':
        return '⚒️';
      case 'Hospital':
        return '🏥';
      default:
        return '🏗️';
    }
  }

  String getBuildingDescription(String type) {
    switch (type) {
      case 'Barracks':
        return '최대 병력 +100, 징병 효율 +2%/Lv';
      case 'Farm':
        return '식량 생산 +5%/Lv';
      case 'Mine':
        return '광물 생산 +5%/Lv';
      case 'Wall':
        return '방어력 +5%/Lv';
      case 'House':
        return '골드 생산 +100/시간/Lv';
      case 'Trading Post':
        return '무역 기능 해금';
      case 'Smithy':
        return '챔피언 공격력 +3%/Lv (최대 30%)';
      case 'Hospital':
        return '패배 시 병력 보존 +5%/Lv (최대 50%)';
      default:
        return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    final resources = userData['resources'] ?? {};
    final reserveTroops = userData['reserve_troops'] ?? 0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('🏰 내정 관리'),
        backgroundColor: Colors.amber[700],
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: loadData),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 자원 현황
                  _buildResourcePanel(resources),
                  const SizedBox(height: 24),

                  // 병력 현황
                  _buildTroopPanel(reserveTroops),
                  const SizedBox(height: 24),

                  // 건물 목록
                  _buildBuildingList(),
                ],
              ),
            ),
    );
  }

  Widget _buildResourcePanel(Map<String, dynamic> resources) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '💰 보유 자원',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 16,
              runSpacing: 8,
              children: [
                _resourceChip('🪙 골드', resources['gold'] ?? 0),
                _resourceChip('🍖 식량', resources['food'] ?? 0),
                _resourceChip('🪵 목재', resources['wood'] ?? 0),
                _resourceChip('⚙️ 철광', resources['iron'] ?? 0),
                _resourceChip('🪨 석재', resources['stone'] ?? 0),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _resourceChip(String label, int amount) {
    return Chip(
      avatar: Text(label.split(' ')[0]),
      label: Text('${label.split(' ')[1]}: $amount'),
      backgroundColor: Colors.grey[200],
    );
  }

  Widget _buildTroopPanel(int reserveTroops) {
    return Card(
      elevation: 4,
      color: Colors.blue[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  '⚔️ 예비 병력',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  '$reserveTroops / $maxTroops',
                  style: const TextStyle(fontSize: 16),
                ),
              ],
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: reserveTroops / maxTroops,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[700]!),
              minHeight: 10,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Text('징병 수량: '),
                Expanded(
                  child: Slider(
                    value: draftAmount.toDouble(),
                    min: 10,
                    max: 100,
                    divisions: 9,
                    label: '$draftAmount',
                    onChanged: (v) => setState(() => draftAmount = v.toInt()),
                  ),
                ),
                Text('$draftAmount명'),
              ],
            ),
            const Text(
              '비용: 식량/목재/철광 각 1씩 (병사 1명당)',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: draftTroops,
              icon: const Icon(Icons.group_add),
              label: Text('$draftAmount명 징병'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[700],
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBuildingList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '🏗️ 건물 목록',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...buildings.map((b) => _buildBuildingCard(b)).toList(),
      ],
    );
  }

  Widget _buildBuildingCard(Map<String, dynamic> building) {
    final type = building['type'] ?? '';
    final level = building['level'] ?? 0;
    final status = building['status'] ?? 'IDLE';
    final finishTime = building['finish_time'];
    final nextCost = building['next_cost'] ?? {};

    final isUpgrading = status == 'UPGRADING';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Text(
          getBuildingIcon(type),
          style: const TextStyle(fontSize: 32),
        ),
        title: Row(
          children: [
            Text(type, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.amber,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text('Lv.$level', style: const TextStyle(fontSize: 12)),
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              getBuildingDescription(type),
              style: TextStyle(color: Colors.grey[600]),
            ),
            if (isUpgrading)
              Text(
                '⏳ 업그레이드 중... ($finishTime)',
                style: const TextStyle(color: Colors.orange),
              )
            else
              Text(
                '비용: 🪵${nextCost['wood'] ?? 0} ⚙️${nextCost['iron'] ?? 0} 🪨${nextCost['stone'] ?? 0}',
                style: const TextStyle(fontSize: 12),
              ),
          ],
        ),
        trailing: isUpgrading
            ? Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  const SizedBox(height: 4),
                  TextButton(
                    onPressed: () => instantFinish(type),
                    child: const Text('⚡즉시완료', style: TextStyle(fontSize: 11)),
                  ),
                ],
              )
            : ElevatedButton(
                onPressed: () => upgradeBuilding(type),
                child: Text(level == 0 ? '건설' : '업그레이드'),
              ),
      ),
    );
  }
}
