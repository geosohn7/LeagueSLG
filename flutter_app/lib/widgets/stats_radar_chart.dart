import 'package:flutter/material.dart';
import 'dart:math' as math;

/// 능력치를 시각화하는 레이더 차트 위젯
class StatsRadarChart extends StatefulWidget {
  final Map<String, dynamic> stats;
  final Color color;

  const StatsRadarChart({super.key, required this.stats, required this.color});

  @override
  State<StatsRadarChart> createState() => _StatsRadarChartState();
}

class _StatsRadarChartState extends State<StatsRadarChart>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _animation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return CustomPaint(
          size: const Size(250, 250),
          painter: RadarChartPainter(
            stats: widget.stats,
            color: widget.color,
            animationValue: _animation.value,
          ),
        );
      },
    );
  }
}

class RadarChartPainter extends CustomPainter {
  final Map<String, dynamic> stats;
  final Color color;
  final double animationValue;

  RadarChartPainter({
    required this.stats,
    required this.color,
    required this.animationValue,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 40;

    // 스탯 목록 (순서 고정)
    final statKeys = ['ATK', 'DEF', 'HP', 'SPATK', 'SPDEF', 'SPD'];
    final statLabels = ['공격', '방어', '체력', '지력', '마방', '속도'];
    final statCount = statKeys.length;

    // 최대값 계산 (정규화를 위해)
    double maxValue = 0;
    for (var key in statKeys) {
      final value = (stats[key] ?? 0).toDouble();
      if (value > maxValue) maxValue = value;
    }
    if (maxValue == 0) maxValue = 100; // 방어적 코딩

    // 배경 그리드 그리기
    _drawGrid(canvas, center, radius, statCount);

    // 스탯 영역 그리기
    _drawStatArea(canvas, center, radius, statKeys, maxValue, statCount);

    // 라벨 그리기
    _drawLabels(canvas, center, radius, statLabels, statCount);
  }

  void _drawGrid(Canvas canvas, Offset center, double radius, int statCount) {
    final gridPaint = Paint()
      ..color = Colors.white.withOpacity(0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // 동심원 그리기 (5단계)
    for (int i = 1; i <= 5; i++) {
      final path = Path();
      final r = radius * (i / 5);

      for (int j = 0; j < statCount; j++) {
        final angle = (2 * math.pi * j / statCount) - math.pi / 2;
        final x = center.dx + r * math.cos(angle);
        final y = center.dy + r * math.sin(angle);

        if (j == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      path.close();
      canvas.drawPath(path, gridPaint);
    }

    // 축 그리기
    for (int i = 0; i < statCount; i++) {
      final angle = (2 * math.pi * i / statCount) - math.pi / 2;
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);
      canvas.drawLine(center, Offset(x, y), gridPaint);
    }
  }

  void _drawStatArea(
    Canvas canvas,
    Offset center,
    double radius,
    List<String> statKeys,
    double maxValue,
    int statCount,
  ) {
    final path = Path();
    final fillPaint = Paint()
      ..color = color.withOpacity(0.3 * animationValue)
      ..style = PaintingStyle.fill;

    final strokePaint = Paint()
      ..color = color.withOpacity(0.8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    for (int i = 0; i < statCount; i++) {
      final statValue = (stats[statKeys[i]] ?? 0).toDouble();
      final normalizedValue = (statValue / maxValue).clamp(0.0, 1.0);
      final r = radius * normalizedValue * animationValue;

      final angle = (2 * math.pi * i / statCount) - math.pi / 2;
      final x = center.dx + r * math.cos(angle);
      final y = center.dy + r * math.sin(angle);

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();

    canvas.drawPath(path, fillPaint);
    canvas.drawPath(path, strokePaint);

    // 포인트 그리기
    for (int i = 0; i < statCount; i++) {
      final statValue = (stats[statKeys[i]] ?? 0).toDouble();
      final normalizedValue = (statValue / maxValue).clamp(0.0, 1.0);
      final r = radius * normalizedValue * animationValue;

      final angle = (2 * math.pi * i / statCount) - math.pi / 2;
      final x = center.dx + r * math.cos(angle);
      final y = center.dy + r * math.sin(angle);

      final pointPaint = Paint()
        ..color = color
        ..style = PaintingStyle.fill;

      canvas.drawCircle(Offset(x, y), 4, pointPaint);
    }
  }

  void _drawLabels(
    Canvas canvas,
    Offset center,
    double radius,
    List<String> labels,
    int statCount,
  ) {
    for (int i = 0; i < statCount; i++) {
      final angle = (2 * math.pi * i / statCount) - math.pi / 2;
      final labelRadius = radius + 25;
      final x = center.dx + labelRadius * math.cos(angle);
      final y = center.dy + labelRadius * math.sin(angle);

      final textPainter = TextPainter(
        text: TextSpan(
          text: labels[i],
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(x - textPainter.width / 2, y - textPainter.height / 2),
      );
    }
  }

  @override
  bool shouldRepaint(RadarChartPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}
