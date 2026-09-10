import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Wraps [child] with four corner brackets — the app's "scan target"
/// motif. Reused later on the upload drop zone.
class ScanFrame extends StatelessWidget {
  final Widget child;
  final double cornerSize;

  const ScanFrame({super.key, required this.child, this.cornerSize = 16});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        _corner(top: 8, left: 8, borders: const [true, true, false, false]),
        _corner(top: 8, right: 8, borders: const [true, false, false, true]),
        _corner(bottom: 8, left: 8, borders: const [false, true, true, false]),
        _corner(bottom: 8, right: 8, borders: const [false, false, true, true]),
      ],
    );
  }

  Widget _corner({
    double? top,
    double? bottom,
    double? left,
    double? right,
    required List<bool> borders, // [top, left, bottom, right]
  }) {
    return Positioned(
      top: top,
      bottom: bottom,
      left: left,
      right: right,
      child: IgnorePointer(
        child: Container(
          width: cornerSize,
          height: cornerSize,
          decoration: BoxDecoration(
            border: Border(
              top: borders[0]
                  ? const BorderSide(color: AppColors.accentPose, width: 2)
                  : BorderSide.none,
              left: borders[1]
                  ? const BorderSide(color: AppColors.accentPose, width: 2)
                  : BorderSide.none,
              bottom: borders[2]
                  ? const BorderSide(color: AppColors.accentPose, width: 2)
                  : BorderSide.none,
              right: borders[3]
                  ? const BorderSide(color: AppColors.accentPose, width: 2)
                  : BorderSide.none,
            ),
          ),
        ),
      ),
    );
  }
}
