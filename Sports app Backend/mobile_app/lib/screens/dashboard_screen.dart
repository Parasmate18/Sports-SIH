import 'package:flutter/material.dart';

import '../services/assessment_service.dart';
import '../services/history_service.dart';
import '../theme/app_colors.dart';
import 'final_result_screen.dart';

class DashboardScreen extends StatefulWidget {
  final String username;
  final String token;

  const DashboardScreen({
    super.key,
    required this.username,
    required this.token,
  });

  @override
  State<DashboardScreen> createState() =>
      _DashboardScreenState();
}

class _DashboardScreenState
    extends State<DashboardScreen> {
  late Future<AssessmentHistoryResponse> _future;

  @override
  void initState() {
    super.initState();

    _future = fetchAssessmentHistory(
      token: widget.token,
    );
  }

  void _refresh() {
    setState(() {
      _future = fetchAssessmentHistory(
        token: widget.token,
      );
    });
  }

  String _formatConfidence(double? value) {
    if (value == null) {
      return '-';
    }

    return '${(value * 100).toStringAsFixed(2)}%';
  }

  String _formatDate(String? value) {
    if (value == null || value.isEmpty) {
      return '-';
    }

    try {
      final date = DateTime.parse(value);

      final day =
          date.day.toString().padLeft(2, '0');

      final month =
          date.month.toString().padLeft(2, '0');

      final year = date.year;

      final hour =
          date.hour.toString().padLeft(2, '0');

      final minute =
          date.minute.toString().padLeft(2, '0');

      return '$day/$month/$year  $hour:$minute';
    } catch (_) {
      return value;
    }
  }

  Color _statusColor(String status) {
    switch (status.toUpperCase()) {
      case 'COMPLETED':
        return AppColors.accentPose;

      case 'IN_PROGRESS':
        return AppColors.accentTrack;

      default:
        return AppColors.textMuted;
    }
  }

  Future<void> _openResult(
    AssessmentHistoryItem assessment,
  ) async {
    if (assessment.status.toUpperCase() !=
        'COMPLETED') {
      return;
    }

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) {
        return const Center(
          child: CircularProgressIndicator(
            color: AppColors.accentPose,
          ),
        );
      },
    );

    try {
      final result = await getSavedAssessmentResult(
        assessmentId: assessment.assessmentId,
        token: widget.token,
      );

      if (!mounted) return;

      Navigator.of(context).pop();

      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => FinalResultScreen(
            result: result,
          ),
        ),
      );
    } on AssessmentException catch (e) {
      if (!mounted) return;

      Navigator.of(context).pop();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.message),
        ),
      );
    } catch (_) {
      if (!mounted) return;

      Navigator.of(context).pop();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Could not load assessment result.',
          ),
        ),
      );
    }
  }

  Widget _buildLatestResult(
    AssessmentHistoryItem assessment,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
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
            'LATEST M1 RESULT',
            style: TextStyle(
              color: AppColors.textMuted,
              fontSize: 11,
              letterSpacing: 1.2,
              fontWeight: FontWeight.w600,
            ),
          ),

          const SizedBox(height: 12),

          Text(
            assessment.talentLevel ?? '-',
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 26,
              fontWeight: FontWeight.w800,
            ),
          ),

          const SizedBox(height: 6),

          Text(
            'Confidence: '
            '${_formatConfidence(assessment.confidence)}',
            style: const TextStyle(
              color: AppColors.textMuted,
              fontSize: 13,
            ),
          ),

          const SizedBox(height: 12),

          Text(
            assessment.recommendedSport ??
                'No recommendation available',
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),

          const SizedBox(height: 16),

          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                _openResult(assessment);
              },
              icon: const Icon(
                Icons.visibility_outlined,
              ),
              label: Text(
                'View Assessment #${assessment.assessmentId}',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAssessmentCard(
    AssessmentHistoryItem assessment,
  ) {
    final completed =
        assessment.status.toUpperCase() ==
            'COMPLETED';

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
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
          Row(
            children: [
              Expanded(
                child: Text(
                  'Assessment #${assessment.assessmentId}',
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),

              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 9,
                  vertical: 5,
                ),
                decoration: BoxDecoration(
                  borderRadius:
                      BorderRadius.circular(20),
                  border: Border.all(
                    color: _statusColor(
                      assessment.status,
                    ),
                  ),
                ),
                child: Text(
                  assessment.status.replaceAll(
                    '_',
                    ' ',
                  ),
                  style: TextStyle(
                    color: _statusColor(
                      assessment.status,
                    ),
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 10),

          Text(
            'Created: '
            '${_formatDate(assessment.createdAt)}',
            style: const TextStyle(
              color: AppColors.textMuted,
              fontSize: 12,
            ),
          ),

          if (completed) ...[
            const SizedBox(height: 6),

            Text(
              'Talent Level: '
              '${assessment.talentLevel ?? '-'}',
              style: const TextStyle(
                color: AppColors.textPrimary,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),

            const SizedBox(height: 4),

            Text(
              'Confidence: '
              '${_formatConfidence(assessment.confidence)}',
              style: const TextStyle(
                color: AppColors.textMuted,
                fontSize: 12,
              ),
            ),

            const SizedBox(height: 10),

            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: () {
                  _openResult(assessment);
                },
                icon: const Icon(
                  Icons.arrow_forward,
                  size: 18,
                ),
                label: const Text(
                  'View Result',
                ),
              ),
            ),
          ],
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
        actions: [
          IconButton(
            onPressed: _refresh,
            icon: const Icon(
              Icons.refresh,
              color: AppColors.accentPose,
            ),
          ),
        ],
      ),
      body: SafeArea(
        child:
            FutureBuilder<AssessmentHistoryResponse>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState !=
                ConnectionState.done) {
              return const Center(
                child: CircularProgressIndicator(
                  color: AppColors.accentPose,
                ),
              );
            }

            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        color: AppColors.accentTrack,
                        size: 40,
                      ),

                      const SizedBox(height: 12),

                      Text(
                        snapshot.error.toString(),
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          color: AppColors.textMuted,
                        ),
                      ),

                      const SizedBox(height: 16),

                      ElevatedButton(
                        onPressed: _refresh,
                        child: const Text(
                          'Try Again',
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }

            final history = snapshot.data;

            if (history == null) {
              return const Center(
                child: Text(
                  'No assessment data available.',
                  style: TextStyle(
                    color: AppColors.textMuted,
                  ),
                ),
              );
            }

            final completed = history.assessments
                .where(
                  (assessment) =>
                      assessment.status
                          .toUpperCase() ==
                      'COMPLETED',
                )
                .toList();

            final latestCompleted =
                completed.isNotEmpty
                    ? completed.first
                    : null;

            return RefreshIndicator(
              onRefresh: () async {
                _refresh();

                await _future;
              },
              child: SingleChildScrollView(
                physics:
                    const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome back, ${widget.username}',
                      style: const TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 13,
                      ),
                    ),

                    const SizedBox(height: 4),

                    const Text(
                      'Your Assessments',
                      style: TextStyle(
                        color:
                            AppColors.textPrimary,
                        fontSize: 22,
                        fontWeight:
                            FontWeight.w700,
                      ),
                    ),

                    const SizedBox(height: 20),

                    Row(
                      children: [
                        _StatChip(
                          label: 'TOTAL',
                          value:
                              '${history.summary.totalAssessments}',
                        ),

                        const SizedBox(width: 10),

                        _StatChip(
                          label: 'COMPLETED',
                          value:
                              '${history.summary.completedAssessments}',
                        ),

                        const SizedBox(width: 10),

                        _StatChip(
                          label: 'PENDING',
                          value:
                              '${history.summary.inProgressAssessments}',
                        ),
                      ],
                    ),

                    if (latestCompleted !=
                        null) ...[
                      const SizedBox(height: 24),

                      _buildLatestResult(
                        latestCompleted,
                      ),
                    ],

                    const SizedBox(height: 28),

                    const Text(
                      'ASSESSMENT HISTORY',
                      style: TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 11,
                        letterSpacing: 1.2,
                        fontWeight:
                            FontWeight.w600,
                      ),
                    ),

                    const SizedBox(height: 12),

                    if (history
                        .assessments.isEmpty)
                      const Text(
                        'No assessments yet.',
                        style: TextStyle(
                          color:
                              AppColors.textMuted,
                        ),
                      )
                    else
                      ...history.assessments.map(
                        _buildAssessmentCard,
                      ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;

  const _StatChip({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(
          vertical: 14,
        ),
        decoration: BoxDecoration(
          color: AppColors.bgSurface,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: AppColors.borderSubtle,
          ),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(
                color: AppColors.textPrimary,
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),

            const SizedBox(height: 4),

            Text(
              label,
              style: const TextStyle(
                color: AppColors.textMuted,
                fontSize: 10,
                letterSpacing: 0.6,
              ),
            ),
          ],
        ),
      ),
    );
  }
}