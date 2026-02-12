import 'dart:convert';
import 'package:http/http.dart' as http;

class GachaService {
  static const String baseUrl = 'http://127.0.0.1:8000';

  /// 가챠 설정 조회
  Future<Map<String, dynamic>> getGachaConfig() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/gacha/config'));
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to load gacha config');
      }
    } catch (e) {
      throw Exception('Error loading gacha config: $e');
    }
  }

  /// 가챠 실행
  Future<Map<String, dynamic>> pullGacha(
    String userId,
    String gachaType,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/gacha/pull'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'user_id': userId, 'gacha_type': gachaType}),
      );

      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else {
        // 에러 메시지 파싱
        final error = json.decode(utf8.decode(response.bodyBytes));
        throw Exception(error['detail'] ?? 'Failed to pull gacha');
      }
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception:', ''));
    }
  }
}
