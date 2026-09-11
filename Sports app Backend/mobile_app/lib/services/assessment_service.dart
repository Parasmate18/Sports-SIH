import 'dart:convert';

import 'package:http/http.dart' as http;

class AssessmentException implements Exception {
  final String message;

  AssessmentException(this.message);
}

class AssessmentSession {
  final int assessmentId;
  final String status;

  AssessmentSession({
    required this.assessmentId,
    required this.status,
  });
}

class FinalAssessmentResult {
  final int assessmentId;
  final String status;

  final Map<String, dynamic> features;
  final Map<String, dynamic> prediction;
  final List<Map<String, dynamic>> recommendedCoaches;

  FinalAssessmentResult({
    required this.assessmentId,
    required this.status,
    required this.features,
    required this.prediction,
    required this.recommendedCoaches,
  });
}

const String assessmentBaseUrl = 'http://172.16.239.150:8000';


// ==========================================================
// CREATE ASSESSMENT
// ==========================================================

Future<AssessmentSession> createAssessment(
  String token,
) async {
  try {
    final response = await http.post(
      Uri.parse(
        '$assessmentBaseUrl/api/v1/assessments',
      ),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw AssessmentException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 201) {
      return AssessmentSession(
        assessmentId: body['assessment_id'],
        status: body['status'],
      );
    }

    if (response.statusCode == 401) {
      throw AssessmentException(
        'Your session has expired. Please sign in again.',
      );
    }

    if (response.statusCode == 403) {
      throw AssessmentException(
        body['detail']?.toString() ??
            'You are not allowed to create an assessment.',
      );
    }

    throw AssessmentException(
      body['detail']?.toString() ??
          'Could not create assessment.',
    );
  } on AssessmentException {
    rethrow;
  } on http.ClientException {
    throw AssessmentException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw AssessmentException(
      'Something went wrong while creating assessment.',
    );
  }
}


// ==========================================================
// FINALIZE ASSESSMENT + RUN M1
// ==========================================================

Future<FinalAssessmentResult> finalizeAssessment({
  required int assessmentId,
  required String token,
  required int age,
  required String gender,
  required double heightCm,
  required double weightKg,
}) async {
  try {
    final response = await http.post(
      Uri.parse(
        '$assessmentBaseUrl/api/v1/assessments/'
        '$assessmentId/finalize',
      ),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'age': age,
        'gender': gender,
        'height_cm': heightCm,
        'weight_kg': weightKg,
      }),
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw AssessmentException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 200) {
      return FinalAssessmentResult(
    assessmentId: body['assessment_id'],
    status: body['status'],
    features: Map<String, dynamic>.from(
    body['features'] ?? {},
   ),
    prediction: Map<String, dynamic>.from(
    body['prediction'] ?? {},
    ),
    recommendedCoaches: List<Map<String, dynamic>>.from(
    (body['recommended_coaches'] ?? []).map(
      (coach) => Map<String, dynamic>.from(coach),
     ),
   ),
  );
    }

    if (response.statusCode == 400) {
      throw AssessmentException(
        body['detail']?.toString() ??
            'Assessment is incomplete.',
      );
    }

    if (response.statusCode == 401) {
      throw AssessmentException(
        'Your session has expired. Please sign in again.',
      );
    }

    if (response.statusCode == 403) {
      throw AssessmentException(
        body['detail']?.toString() ??
            'You are not allowed to finalize this assessment.',
      );
    }

    if (response.statusCode == 500) {
      throw AssessmentException(
        body['detail']?.toString() ??
            'Could not generate final assessment result.',
      );
    }

    throw AssessmentException(
      body['detail']?.toString() ??
          'Could not finalize assessment.',
    );
  } on AssessmentException {
    rethrow;
  } on http.ClientException {
    throw AssessmentException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw AssessmentException(
      'Something went wrong while finalizing assessment.',
    );
  }
}

// ==========================================================
// GET SAVED ASSESSMENT RESULT
// ==========================================================

Future<FinalAssessmentResult> getSavedAssessmentResult({
  required int assessmentId,
  required String token,
}) async {
  try {
    final response = await http.get(
      Uri.parse(
        '$assessmentBaseUrl/api/v1/assessments/'
        '$assessmentId/result',
      ),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw AssessmentException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 200) {
      return FinalAssessmentResult(
     assessmentId: body['assessment_id'],
     status: body['status'],
    features: Map<String, dynamic>.from(
    body['features'] ?? {},
    ),
    prediction: Map<String, dynamic>.from(
    body['prediction'] ?? {},
    ),
    recommendedCoaches: List<Map<String, dynamic>>.from(
    (body['recommended_coaches'] ?? []).map(
      (coach) => Map<String, dynamic>.from(coach),
    ),
  ),
);
    }

    if (response.statusCode == 401) {
      throw AssessmentException(
        'Your session has expired. Please sign in again.',
      );
    }

    if (response.statusCode == 403) {
      throw AssessmentException(
        'You are not allowed to view this assessment.',
      );
    }

    if (response.statusCode == 404) {
      throw AssessmentException(
        'Saved assessment result not found.',
      );
    }

    throw AssessmentException(
      body['detail']?.toString() ??
          'Could not load saved assessment result.',
    );
  } on AssessmentException {
    rethrow;
  } on http.ClientException {
    throw AssessmentException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw AssessmentException(
      'Something went wrong while loading the saved result.',
    );
  }
}