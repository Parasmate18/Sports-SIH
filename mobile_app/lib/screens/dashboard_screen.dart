import 'package:flutter/material.dart';

import '../services/history_service.dart';
import '../theme/app_colors.dart';
import '../widgets/attempt_history_card.dart';
import '../widgets/score_bar_chart.dart';

class DashboardScreen extends StatefulWidget {
  final String username;
  const DashboardScreen({super.key, required this.username});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late Future<List<AttemptRecord>> _future;

  @override
  void initState() {
    super.initState();
    _future = fetchAttemptHistory();
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
        child: FutureBuilder<List<AttemptRecord>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(
                child: CircularProgressIndicator(color: AppColors.accentPose),
              );
            }
            final attempts = snapshot.data ?? [];
            if (attempts.isEmpty) {
              return const Center(
                child: Text(
                  'No attempts yet.',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              );
            }

            final avgScore =
                (attempts.map((a) => a.score).reduce((a, b) => a + b) /
                        attempts.length)
                    .round();
            final bestScore = attempts
                .map((a) => a.score)
                .reduce((a, b) => a > b ? a : b);

            return SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
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
                    'Your Progress',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 20),

                  Row(
                    children: [
                      _StatChip(label: 'ATTEMPTS', value: '${attempts.length}'),
                      const SizedBox(width: 10),
                      _StatChip(label: 'AVG SCORE', value: '$avgScore'),
                      const SizedBox(width: 10),
                      _StatChip(label: 'BEST', value: '$bestScore'),
                    ],
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    'SCORE TREND',
                    style: TextStyle(
                      color: AppColors.textMuted,
                      fontSize: 11,
                      letterSpacing: 1.2,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.borderSubtle),
                    ),
                    child: ScoreBarChart(attempts: attempts),
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    'RECENT ATTEMPTS',
                    style: TextStyle(
                      color: AppColors.textMuted,
                      fontSize: 11,
                      letterSpacing: 1.2,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ...attempts.map((a) => AttemptHistoryCard(attempt: a)),
                ],
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
  const _StatChip({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: AppColors.bgSurface,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppColors.borderSubtle),
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
