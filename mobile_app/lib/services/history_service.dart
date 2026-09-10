import 'dart:convert';

import 'package:http/http.dart' as http;

class HistoryException implements Exception {
  final String message;

  HistoryException(this.message);

  @override
  String toString() => message;
}

class AssessmentHistoryItem {
  final int assessmentId;
  final String status;
  final String? createdAt;
  final String? completedAt;
  final String? talentLevel;
  final double? confidence;
  final String? recommendedSport;
  final String? modelVersion;

  AssessmentHistoryItem({
    required this.assessmentId,
    required this.status,
    this.createdAt,
    this.completedAt,
    this.talentLevel,
    this.confidence,
    this.recommendedSport,
    this.modelVersion,
  });

  factory AssessmentHistoryItem.fromJson(
    Map<String, dynamic> json,
  ) {
    return AssessmentHistoryItem(
      assessmentId: json['assessment_id'],
      status: json['status'] ?? '',
      createdAt: json['created_at']?.toString(),
      completedAt: json['completed_at']?.toString(),
      talentLevel: json['talent_level']?.toString(),
      confidence: json['confidence'] == null
          ? null
          : (json['confidence'] as num).toDouble(),
      recommendedSport:
          json['recommended_sport']?.toString(),
      modelVersion: json['model_version']?.toString(),
    );
  }
}

class AssessmentHistorySummary {
  final int totalAssessments;
  final int completedAssessments;
  final int inProgressAssessments;

  AssessmentHistorySummary({
    required this.totalAssessments,
    required this.completedAssessments,
    required this.inProgressAssessments,
  });

  factory AssessmentHistorySummary.fromJson(
    Map<String, dynamic> json,
  ) {
    return AssessmentHistorySummary(
      totalAssessments:
          json['total_assessments'] ?? 0,
      completedAssessments:
          json['completed_assessments'] ?? 0,
      inProgressAssessments:
          json['in_progress_assessments'] ?? 0,
    );
  }
}

class AssessmentHistoryResponse {
  final AssessmentHistorySummary summary;
  final List<AssessmentHistoryItem> assessments;

  AssessmentHistoryResponse({
    required this.summary,
    required this.assessments,
  });
}

const String historyBaseUrl = 'http://172.16.239.150:8000';

Future<AssessmentHistoryResponse> fetchAssessmentHistory({
  required String token,
}) async {
  try {
    final response = await http.get(
      Uri.parse(
        '$historyBaseUrl/api/v1/assessments/history/all',
      ),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw HistoryException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 200) {
      final summary =
          AssessmentHistorySummary.fromJson(
        Map<String, dynamic>.from(
          body['summary'] ?? {},
        ),
      );

      final rawAssessments =
          body['assessments'] as List? ?? [];

      final assessments = rawAssessments
          .map(
            (item) => AssessmentHistoryItem.fromJson(
              Map<String, dynamic>.from(item),
            ),
          )
          .toList();

      return AssessmentHistoryResponse(
        summary: summary,
        assessments: assessments,
      );
    }

    if (response.statusCode == 401) {
      throw HistoryException(
        'Your session has expired. Please sign in again.',
      );
    }

    if (response.statusCode == 403) {
      throw HistoryException(
        'You are not allowed to view assessment history.',
      );
    }

    throw HistoryException(
      body['detail']?.toString() ??
          'Could not load assessment history.',
    );
  } on HistoryException {
    rethrow;
  } on http.ClientException {
    throw HistoryException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw HistoryException(
      'Something went wrong while loading assessment history.',
    );
  }
}