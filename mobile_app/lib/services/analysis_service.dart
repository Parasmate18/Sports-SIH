import 'dart:math';

import 'package:image_picker/image_picker.dart';

class MetricItem {
  final String label;
  final String value;
  const MetricItem(this.label, this.value);
}

class AnalysisResult {
  final String exercise;
  final String fileName;
  final int score;
  final String grade;
  final List<MetricItem> metrics;
  final List<String> feedback;

  AnalysisResult({
    required this.exercise,
    required this.fileName,
    required this.score,
    required this.grade,
    required this.metrics,
    required this.feedback,
  });
}

class AnalysisException implements Exception {
  final String message;
  AnalysisException(this.message);
}

const bool useMockAnalysis = true;

Future<AnalysisResult> analyzeVideo(XFile file, String exercise) async {
  if (useMockAnalysis) {
    await Future.delayed(const Duration(milliseconds: 1800));
    if (Random().nextDouble() < 0.05) {
      throw AnalysisException(
        'Mock failure: pose could not be detected. Try better lighting.',
      );
    }
    return AnalysisResult(
      exercise: exercise,
      fileName: file.name,
      score: 78,
      grade: 'B+',
      metrics: const [
        MetricItem('Jump Height', '42 cm'),
        MetricItem('Takeoff Angle', '86°'),
        MetricItem('Symmetry', '91%'),
      ],
      feedback: const [
        'Good extension at takeoff.',
        'Landing knee flexion is slightly shallow — bend more on impact.',
      ],
    );
  }

  // Real backend call goes here later, e.g. multipart upload with `http` or `dio`.
  throw AnalysisException('Backend not connected yet.');
}
