import 'package:flutter/material.dart';

import '../services/assessment_service.dart';
import '../theme/app_colors.dart';

class FinalResultScreen extends StatelessWidget {
  final FinalAssessmentResult result;

  const FinalResultScreen({
    super.key,
    required this.result,
  });

  String _formatConfidence(dynamic value) {
    if (value is num) {
      return '${(value * 100).toStringAsFixed(2)}%';
    }
    return '-';
  }

  String _formatFeature(String key, dynamic value) {
    if (value == null) return '-';

    switch (key) {
      case 'height_cm':
        return '$value cm';
      case 'weight_kg':
        return '$value kg';
      case 'running_50m_seconds':
        return '$value sec';
      case 'plank_duration_seconds':
        return '$value sec';
      case 'vertical_jump_cm':
        return '$value cm';
      default:
        return value.toString();
    }
  }

  String _featureLabel(String key) {
    switch (key) {
      case 'age':
        return 'Age';
      case 'gender':
        return 'Gender';
      case 'height_cm':
        return 'Height';
      case 'weight_kg':
        return 'Weight';
      case 'pushup_count':
        return 'Push-ups';
      case 'squat_count':
        return 'Squats';
      case 'deadlift_reps':
        return 'Deadlift Reps';
      case 'running_50m_seconds':
        return '50 m Running';
      case 'situp_count':
        return 'Sit-ups';
      case 'plank_duration_seconds':
        return 'Plank Duration';
      case 'vertical_jump_cm':
        return 'Vertical Jump';
      default:
        return key;
    }
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Text(
        title,
        style: const TextStyle(
          color: AppColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _infoCard({
    required String label,
    required String value,
    IconData? icon,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: AppColors.borderSubtle,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (icon != null) ...[
            Icon(
              icon,
              color: AppColors.accentPose,
              size: 22,
            ),
            const SizedBox(width: 12),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _listCard({
    required String title,
    required List<dynamic> items,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: AppColors.borderSubtle,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 15,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          if (items.isEmpty)
            const Text(
              '-',
              style: TextStyle(
                color: AppColors.textMuted,
              ),
            )
          else
            ...items.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '• ',
                      style: TextStyle(
                        color: AppColors.accentPose,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        item.toString(),
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final prediction = result.prediction;
    final features = result.features;

    final strengths =
        List<dynamic>.from(prediction['strengths'] ?? []);

    final needsImprovement =
        List<dynamic>.from(prediction['needs_improvement'] ?? []);

    final talentLevel =
        prediction['talent_level']?.toString() ?? '-';

    final confidence =
        _formatConfidence(prediction['confidence']);

    final recommendedSport =
        prediction['recommended_sport']?.toString() ?? '-';

    final modelVersion =
        prediction['model_version']?.toString() ?? '-';

    final warning =
        prediction['warning']?.toString() ?? '';

    return Scaffold(
      backgroundColor: AppColors.bgBase,
      appBar: AppBar(
        backgroundColor: AppColors.bgBase,
        elevation: 0,
        title: const Text(
          'Final Assessment Result',
          style: TextStyle(
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: AppColors.bgSurface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.accentPose,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Assessment Completed',
                      style: TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      talentLevel,
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 30,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Confidence: $confidence',
                      style: const TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              _sectionTitle('Prediction'),

              _infoCard(
                label: 'Recommended Sport',
                value: recommendedSport,
                icon: Icons.sports,
              ),

              _infoCard(
                label: 'Model Version',
                value: modelVersion,
                icon: Icons.memory,
              ),

              const SizedBox(height: 10),

              _listCard(
                title: 'Strengths',
                items: strengths,
              ),

              _listCard(
                title: 'Needs Improvement',
                items: needsImprovement,
              ),

              const SizedBox(height: 10),

              _sectionTitle('Assessment Features'),

              ...features.entries.map(
                (entry) => _infoCard(
                  label: _featureLabel(entry.key),
                  value: _formatFeature(
                    entry.key,
                    entry.value,
                  ),
                ),
              ),

              if (warning.isNotEmpty) ...[
                const SizedBox(height: 14),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppColors.bgSurface,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: AppColors.borderSubtle,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Important Notice',
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        warning,
                        style: const TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              const SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accentTrack,
                    padding: const EdgeInsets.symmetric(
                      vertical: 15,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Back to Assessment',
                    style: TextStyle(
                      color: AppColors.textOnAccent,
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