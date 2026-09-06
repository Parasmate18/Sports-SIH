import 'package:flutter/material.dart';

import '../services/analysis_service.dart';
import '../theme/app_colors.dart';
import '../widgets/feedback_card.dart';
import '../widgets/metric_card.dart';
import '../widgets/scan_frame.dart';

class ResultsScreen extends StatelessWidget {
  final AnalysisResult result;
  const ResultsScreen({super.key, required this.result});

  Color _gradeColor() {
    if (result.score >= 85) return AppColors.accentPose;
    if (result.score >= 60) return AppColors.accentWarn;
    return AppColors.accentTrack;
  }

  String _exerciseLabel() {
    switch (result.exercise) {
      case 'vertical_jump':
        return 'Vertical Jump';
      case 'shuttle_run':
        return 'Shuttle Run';
      case 'sit_ups':
        return 'Sit-Ups';
      case 'sit_and_reach':
        return 'Sit and Reach';
      default:
        return result.exercise;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgBase,
      appBar: AppBar(
        title: const Text(
          'ATHLETIQ',
          style: TextStyle(fontWeight: FontWeight.w700, letterSpacing: 1.1),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _exerciseLabel(),
                style: const TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 13,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Attempt Results',
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 24),

              Center(
                child: ScanFrame(
                  child: Container(
                    width: 180,
                    height: 180,
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      shape: BoxShape.circle,
                      border: Border.all(color: _gradeColor(), width: 3),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '${result.score}',
                          style: TextStyle(
                            color: _gradeColor(),
                            fontSize: 44,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'GRADE ${result.grade}',
                          style: const TextStyle(
                            color: AppColors.textMuted,
                            fontSize: 12,
                            letterSpacing: 1.0,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 28),

              const Text(
                'METRICS',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 11,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 1.6,
                children: result.metrics
                    .map((m) => MetricCard(metric: m))
                    .toList(),
              ),
              const SizedBox(height: 24),

              FeedbackCard(feedback: result.feedback),
              const SizedBox(height: 28),

              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AppColors.accentPose),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Submit another attempt',
                    style: TextStyle(
                      color: AppColors.accentPose,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
