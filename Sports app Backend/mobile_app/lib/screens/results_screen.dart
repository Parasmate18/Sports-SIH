import 'package:flutter/material.dart';

import '../services/analysis_service.dart';
import '../theme/app_colors.dart';
import '../widgets/scan_frame.dart';

class ResultsScreen extends StatelessWidget {
  final AnalysisResult result;

  const ResultsScreen({
    super.key,
    required this.result,
  });

  String _exerciseLabel() {
    switch (result.exercise) {
      case 'pushup':
        return 'Push-up';
      case 'squat':
        return 'Squat';
      case 'deadlift':
        return 'Deadlift';
      case 'running':
        return '50 m Running';
      case 'situp':
        return 'Sit-up';
      case 'plank':
        return 'Plank';
      case 'vertical_jump':
        return 'Vertical Jump';
      default:
        return result.exercise;
    }
  }

  Color _statusColor() {
    if (result.status.toUpperCase() == 'SUCCESS') {
      return AppColors.accentPose;
    }

    return AppColors.accentWarn;
  }

  String _formatValue(dynamic value) {
    if (value == null) {
      return '-';
    }

    if (value is double) {
      return value.toStringAsFixed(2);
    }

    return value.toString();
  }

  Widget _infoCard({
  required String label,
  required String value,
}) {
  return Container(
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(
      color: AppColors.bgSurface,
      borderRadius: BorderRadius.circular(8),
      border: Border.all(
        color: AppColors.borderSubtle,
      ),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: AppColors.textMuted,
            fontSize: 11,
          ),
        ),
        const SizedBox(height: 6),
        Flexible(
          child: Text(
            value,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 15,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ],
    ),
  );
}
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgBase,
      appBar: AppBar(
        backgroundColor: AppColors.bgBase,
        elevation: 0,
        title: const Text(
          'ATHLETIQ',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            letterSpacing: 1.1,
          ),
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
                    width: 190,
                    height: 190,
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: _statusColor(),
                        width: 3,
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '${result.validReps}',
                          style: TextStyle(
                            color: _statusColor(),
                            fontSize: 44,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'VALID REPS',
                          style: TextStyle(
                            color: AppColors.textMuted,
                            fontSize: 11,
                            letterSpacing: 1.0,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          result.status.toUpperCase(),
                          style: TextStyle(
                            color: _statusColor(),
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 28),

              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 1.35,
                children: [
                  _infoCard(
                    label: 'Assessment ID',
                    value: result.assessmentId.toString(),
                  ),
                  _infoCard(
                    label: 'Session ID',
                    value: result.sessionId.toString(),
                  ),
                  _infoCard(
                    label: 'Measurement',
                    value: _formatValue(result.measurement),
                  ),
                  _infoCard(
                      label: 'Video',
                      value: 'Uploaded',
                    ),
                ],
              ),

              const SizedBox(height: 28),

              const Text(
                'CV FEATURES',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 11,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 10),

              if (result.features.isEmpty)
                const Text(
                  'No feature values returned.',
                  style: TextStyle(
                    color: AppColors.textMuted,
                  ),
                )
              else
                ...result.features.entries.map(
                  (entry) => Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: AppColors.borderSubtle,
                      ),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            entry.key,
                            style: const TextStyle(
                              color: AppColors.textMuted,
                              fontSize: 12,
                            ),
                          ),
                        ),
                        Text(
                          _formatValue(entry.value),
                          style: const TextStyle(
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              const SizedBox(height: 20),

              const Text(
                'QUALITY',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 11,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 10),

              if (result.quality.isEmpty)
                const Text(
                  'No quality information returned.',
                  style: TextStyle(
                    color: AppColors.textMuted,
                  ),
                )
              else
                ...result.quality.entries.map(
                  (entry) => Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: AppColors.borderSubtle,
                      ),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            entry.key,
                            style: const TextStyle(
                              color: AppColors.textMuted,
                              fontSize: 12,
                            ),
                          ),
                        ),
                        Text(
                          _formatValue(entry.value),
                          style: const TextStyle(
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              const SizedBox(height: 28),

              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(
                      color: AppColors.accentPose,
                    ),
                    padding: const EdgeInsets.symmetric(
                      vertical: 14,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Submit another exercise',
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