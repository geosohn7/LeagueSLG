import 'dart:async';
import 'package:flutter/material.dart';

/// 전투 시뮬레이션 화면
class BattleScreen extends StatefulWidget {
  final Map<String, dynamic> battleData;

  const BattleScreen({super.key, required this.battleData});

  @override
  State<BattleScreen> createState() => _BattleScreenState();
}

class _BattleScreenState extends State<BattleScreen>
    with SingleTickerProviderStateMixin {
  // 전투 데이터
  late String leftChampion;
  late String rightChampion;
  late double leftMaxHp;
  late double rightMaxHp;
  late double leftCurrentHp;
  late double rightCurrentHp;
  late List<dynamic> battleLogs;
  late String winner;

  // 애니메이션 상태
  int currentLogIndex = 0;
  bool isPlaying = false;
  bool isFinished = false;
  Timer? playbackTimer;
  String currentMessage = '';

  // 공격 애니메이션
  bool leftAttacking = false;
  bool rightAttacking = false;

  // 데미지 표시
  String? leftDamageText;
  String? rightDamageText;

  @override
  void initState() {
    super.initState();
    _initializeBattleData();
    // 0.5초 후 자동으로 전투 시작
    Future.delayed(const Duration(milliseconds: 500), () {
      _startBattle();
    });
  }

  void _initializeBattleData() {
    leftChampion = widget.battleData['left']['name'];
    rightChampion = widget.battleData['right']['name'];
    leftMaxHp = widget.battleData['left']['max_hp'].toDouble();
    rightMaxHp = widget.battleData['right']['max_hp'].toDouble();
    leftCurrentHp = leftMaxHp;
    rightCurrentHp = rightMaxHp;
    battleLogs = widget.battleData['logs'];
    winner = widget.battleData['winner'];
  }

  void _startBattle() {
    setState(() {
      isPlaying = true;
    });

    playbackTimer = Timer.periodic(const Duration(milliseconds: 1000), (timer) {
      if (currentLogIndex >= battleLogs.length) {
        timer.cancel();
        _finishBattle();
        return;
      }

      _playNextLog();
      currentLogIndex++;
    });
  }

  void _playNextLog() {
    final log = battleLogs[currentLogIndex];
    final actor = log['actor'];
    final damage = log['damage'];

    setState(() {
      currentMessage = log['message'];

      // HP 업데이트
      leftCurrentHp = log['left_hp'].toDouble();
      rightCurrentHp = log['right_hp'].toDouble();

      // 공격 애니메이션
      if (actor == leftChampion) {
        leftAttacking = true;
        rightDamageText = '-${damage.toInt()}';
        Future.delayed(const Duration(milliseconds: 300), () {
          setState(() {
            leftAttacking = false;
          });
        });
        Future.delayed(const Duration(milliseconds: 800), () {
          setState(() {
            rightDamageText = null;
          });
        });
      } else {
        rightAttacking = true;
        leftDamageText = '-${damage.toInt()}';
        Future.delayed(const Duration(milliseconds: 300), () {
          setState(() {
            rightAttacking = false;
          });
        });
        Future.delayed(const Duration(milliseconds: 800), () {
          setState(() {
            leftDamageText = null;
          });
        });
      }
    });
  }

  void _finishBattle() {
    setState(() {
      isPlaying = false;
      isFinished = true;
    });
  }

  @override
  void dispose() {
    playbackTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.blue[900]!, Colors.purple[900]!],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // 상단 HP 바
              _buildTopBar(),

              // 중앙 전투 구역
              Expanded(child: _buildBattleStage()),

              // 하단 로그 영역
              _buildBottomLog(),

              // 결과 화면 (전투 종료 시)
              if (isFinished) _buildResultOverlay(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          // 왼쪽 챔피언 HP
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  leftChampion,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                _buildHpBar(leftCurrentHp, leftMaxHp, Colors.green),
                Text(
                  '${leftCurrentHp.toInt()} / ${leftMaxHp.toInt()}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          const Text(
            'VS',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 16),
          // 오른쪽 챔피언 HP
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  rightChampion,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                _buildHpBar(rightCurrentHp, rightMaxHp, Colors.red),
                Text(
                  '${rightCurrentHp.toInt()} / ${rightMaxHp.toInt()}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHpBar(double current, double max, Color color) {
    final percentage = (current / max).clamp(0.0, 1.0);
    return Container(
      height: 20,
      decoration: BoxDecoration(
        color: Colors.black38,
        borderRadius: BorderRadius.circular(10),
      ),
      child: FractionallySizedBox(
        alignment: Alignment.centerLeft,
        widthFactor: percentage,
        child: Container(
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
    );
  }

  Widget _buildBattleStage() {
    return Stack(
      children: [
        // 배경 그리드
        Center(
          child: Container(
            width: 600,
            height: 400,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.white24),
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        // 왼쪽 챔피언
        Positioned(
          left: 100,
          top: 150,
          child: _buildChampionSprite(
            leftChampion,
            leftAttacking,
            leftDamageText,
            true,
          ),
        ),
        // 오른쪽 챔피언
        Positioned(
          right: 100,
          top: 150,
          child: _buildChampionSprite(
            rightChampion,
            rightAttacking,
            rightDamageText,
            false,
          ),
        ),
      ],
    );
  }

  Widget _buildChampionSprite(
    String name,
    bool isAttacking,
    String? damageText,
    bool isLeft,
  ) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      transform: Matrix4.translationValues(
        isAttacking ? (isLeft ? 20 : -20) : 0,
        0,
        0,
      ),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // 챔피언 아이콘 (임시로 원형 아바타 사용)
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isLeft ? Colors.blue[600] : Colors.red[600],
              border: Border.all(color: Colors.white, width: 3),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Center(
              child: Text(
                name[0],
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          // 데미지 텍스트
          if (damageText != null)
            Positioned(
              top: -30,
              left: 30,
              child: TweenAnimationBuilder(
                tween: Tween<double>(begin: 0, end: 1),
                duration: const Duration(milliseconds: 800),
                builder: (context, value, child) {
                  return Transform.translate(
                    offset: Offset(0, -20 * value),
                    child: Opacity(
                      opacity: 1 - value,
                      child: Text(
                        damageText,
                        style: const TextStyle(
                          color: Colors.red,
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          shadows: [Shadow(color: Colors.black, blurRadius: 4)],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildBottomLog() {
    return Container(
      height: 100,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.5),
        border: const Border(top: BorderSide(color: Colors.white24)),
      ),
      child: Center(
        child: Text(
          currentMessage,
          style: const TextStyle(color: Colors.white, fontSize: 16),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  Widget _buildResultOverlay() {
    final isVictory = winner == leftChampion;
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              isVictory ? '승리!' : '패배...',
              style: TextStyle(
                color: isVictory ? Colors.yellow : Colors.red,
                fontSize: 64,
                fontWeight: FontWeight.bold,
                shadows: const [Shadow(color: Colors.black, blurRadius: 10)],
              ),
            ),
            const SizedBox(height: 32),
            Text(
              '승자: $winner',
              style: const TextStyle(color: Colors.white, fontSize: 24),
            ),
            const SizedBox(height: 48),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 48,
                  vertical: 16,
                ),
              ),
              child: const Text('확인', style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }
}
