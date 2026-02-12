import 'package:flutter/material.dart';

/// 히어로 애니메이션을 사용한 페이지 전환
class HeroPageRoute<T> extends PageRoute<T> {
  HeroPageRoute({required this.builder, RouteSettings? settings})
    : super(settings: settings);

  final WidgetBuilder builder;

  @override
  Color? get barrierColor => null;

  @override
  String? get barrierLabel => null;

  @override
  bool get maintainState => true;

  @override
  Duration get transitionDuration => const Duration(milliseconds: 400);

  @override
  Widget buildPage(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
  ) {
    return builder(context);
  }

  @override
  Widget buildTransitions(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    // 페이드 + 슬라이드 애니메이션
    const begin = Offset(0.0, 0.1);
    const end = Offset.zero;
    const curve = Curves.easeOutCubic;

    var tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));

    var offsetAnimation = animation.drive(tween);
    var fadeAnimation = CurvedAnimation(
      parent: animation,
      curve: Curves.easeIn,
    );

    return SlideTransition(
      position: offsetAnimation,
      child: FadeTransition(opacity: fadeAnimation, child: child),
    );
  }
}

/// 스케일 애니메이션을 사용한 페이지 전환
class ScalePageRoute<T> extends PageRoute<T> {
  ScalePageRoute({required this.builder, RouteSettings? settings})
    : super(settings: settings);

  final WidgetBuilder builder;

  @override
  Color? get barrierColor => Colors.black54;

  @override
  String? get barrierLabel => null;

  @override
  bool get maintainState => true;

  @override
  bool get opaque => false;

  @override
  Duration get transitionDuration => const Duration(milliseconds: 300);

  @override
  Widget buildPage(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
  ) {
    return builder(context);
  }

  @override
  Widget buildTransitions(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    // 스케일 + 페이드 애니메이션
    var scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(parent: animation, curve: Curves.easeOutBack));

    var fadeAnimation = CurvedAnimation(
      parent: animation,
      curve: Curves.easeIn,
    );

    return ScaleTransition(
      scale: scaleAnimation,
      child: FadeTransition(opacity: fadeAnimation, child: child),
    );
  }
}
