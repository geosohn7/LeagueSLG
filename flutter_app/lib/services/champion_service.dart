import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/champion_model.dart';

class ChampionService {
  static const String baseUrl = 'http://localhost:8000';

  /// 보유 장수 목록 조회
  Future<List<Champion>> getChampionRoster(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/user/$userId/champions'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> championsJson = data['champions'] ?? [];

        return championsJson.map((json) => Champion.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load champions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error loading champions: $e');
    }
  }

  /// 장수 상세 정보 조회
  Future<ChampionDetail> getChampionDetail(
    String userId,
    int championId,
  ) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/user/$userId/champion/$championId'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ChampionDetail.fromJson(data);
      } else {
        throw Exception(
          'Failed to load champion detail: ${response.statusCode}',
        );
      }
    } catch (e) {
      throw Exception('Error loading champion detail: $e');
    }
  }
}
