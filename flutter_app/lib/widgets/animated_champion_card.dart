import 'package:flutter/material.dart';

/// 애니메이션이 적용된 장수 카드 위젯
class AnimatedChampionCard extends StatefulWidget {
  final String name;
  final int level;
  final String faction;
  final Color factionColor;
  final VoidCallback onTap;
  final int index;

  const AnimatedChampionCard({
    super.key,
    required this.name,
    required this.level,
    required this.faction,
    required this.factionColor,
    required this.onTap,
    required this.index,
  });

  @override
  State<AnimatedChampionCard> createState() => _AnimatedChampionCardState();
}

class _AnimatedChampionCardState extends State<AnimatedChampionCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    // 진입 애니메이션 (순차적으로 나타남)
    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Interval(0.0, 0.6, curve: Curves.easeOutBack),
      ),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.4, curve: Curves.easeIn),
      ),
    );

    _slideAnimation =
        Tween<Offset>(begin: const Offset(0, 0.3), end: Offset.zero).animate(
          CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
          ),
        );

    // 순차적 진입을 위한 딜레이
    Future.delayed(Duration(milliseconds: widget.index * 50), () {
      if (mounted) {
        _controller.forward();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: ScaleTransition(
          scale: _scaleAnimation,
          child: MouseRegion(
            onEnter: (_) => setState(() => _isHovered = true),
            onExit: (_) => setState(() => _isHovered = false),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              transform: Matrix4.identity()
                ..scale(_isHovered ? 1.05 : 1.0)
                ..rotateZ(_isHovered ? -0.02 : 0.0),
              child: GestureDetector(
                onTap: widget.onTap,
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        widget.factionColor.withOpacity(0.8),
                        widget.factionColor.withOpacity(0.6),
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: _isHovered
                            ? widget.factionColor.withOpacity(0.5)
                            : Colors.black.withOpacity(0.3),
                        blurRadius: _isHovered ? 16 : 8,
                        offset: Offset(0, _isHovered ? 8 : 4),
                        spreadRadius: _isHovered ? 2 : 0,
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Stack(
                      children: [
                        // 반짝이는 효과
                        if (_isHovered)
                          Positioned.fill(
                            child: AnimatedOpacity(
                              duration: const Duration(milliseconds: 300),
                              opacity: _isHovered ? 1.0 : 0.0,
                              child: Container(
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    begin: Alignment.topLeft,
                                    end: Alignment.bottomRight,
                                    colors: [
                                      Colors.white.withOpacity(0.3),
                                      Colors.transparent,
                                      Colors.white.withOpacity(0.1),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),

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
                                  'Lv.${widget.level}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                              ),

                              const Spacer(),

                              // 장수 초상화
                              Center(
                                child: AnimatedContainer(
                                  duration: const Duration(milliseconds: 200),
                                  width: _isHovered ? 90 : 80,
                                  height: _isHovered ? 90 : 80,
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.3),
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: Colors.white,
                                      width: 3,
                                    ),
                                    boxShadow: _isHovered
                                        ? [
                                            BoxShadow(
                                              color: Colors.white.withOpacity(
                                                0.5,
                                              ),
                                              blurRadius: 12,
                                              spreadRadius: 2,
                                            ),
                                          ]
                                        : [],
                                  ),
                                  child: Icon(
                                    Icons.person,
                                    size: _isHovered ? 55 : 50,
                                    color: Colors.white,
                                  ),
                                ),
                              ),

                              const Spacer(),

                              // 장수 이름
                              Center(
                                child: Text(
                                  widget.name,
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: _isHovered ? 17 : 16,
                                    fontWeight: FontWeight.bold,
                                    shadows: const [
                                      Shadow(
                                        color: Colors.black,
                                        blurRadius: 4,
                                      ),
                                    ],
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),

                              const SizedBox(height: 4),

                              // 진영
                              Center(
                                child: Text(
                                  widget.faction,
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.9),
                                    fontSize: 12,
                                    shadows: const [
                                      Shadow(
                                        color: Colors.black,
                                        blurRadius: 2,
                                      ),
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
              ),
            ),
          ),
        ),
      ),
    );
  }
}
