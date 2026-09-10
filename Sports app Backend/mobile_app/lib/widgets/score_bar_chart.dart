import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../services/history_service.dart';

class ScoreBarChart extends StatelessWidget {
  final List<AttemptRecord> attempts;
  const ScoreBarChart({super.key, required this.attempts});

  Color _barColor(int score) {
    if (score >= 85) return AppColors.accentPose;
    if (score >= 60) return AppColors.accentWarn;
    return AppColors.accentTrack;
  }

  @override
  Widget build(BuildContext context) {
    final ordered = attempts.reversed
        .toList(); // oldest to newest, left to right
    const maxBarHeight = 80.0;
    return SizedBox(
      height: 140,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: ordered.map((a) {
          final barHeight = maxBarHeight * (a.score.clamp(0, 100) / 100);
          return Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Text(
                    '${a.score}',
                    style: TextStyle(
                      color: _barColor(a.score),
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    height: barHeight,
                    decoration: BoxDecoration(
                      color: _barColor(a.score),
                      borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(4),
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    a.date,
                    style: const TextStyle(
                      color: AppColors.textMuted,
                      fontSize: 9,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
