import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

class MetricItem {
  final String label;
  final String value;

  const MetricItem(this.label, this.value);
}

class AnalysisResult {
  final int assessmentId;
  final int sessionId;
  final String exercise;
  final String fileName;
  final String status;
  final int validReps;
  final dynamic measurement;
  final Map<String, dynamic> features;
  final Map<String, dynamic> quality;

  AnalysisResult({
    required this.assessmentId,
    required this.sessionId,
    required this.exercise,
    required this.fileName,
    required this.status,
    required this.validReps,
    required this.measurement,
    required this.features,
    required this.quality,
  });
}

class AnalysisException implements Exception {
  final String message;

  AnalysisException(this.message);
}

const String analysisBaseUrl = 'http://127.0.0.1:8000';

Future<AnalysisResult> analyzeVideo({
  required XFile file,
  required String exercise,
  required int assessmentId,
  required String token,
  double? heightCm,
}) async {
  try {
    final uri = Uri.parse(
      '$analysisBaseUrl/api/v1/assessments/$assessmentId/exercises/$exercise',
    );

    final request = http.MultipartRequest(
      'POST',
      uri,
    );

    request.headers['Authorization'] = 'Bearer $token';
    if (exercise == 'vertical_jump' && heightCm != null) {
    request.fields['height_cm'] = heightCm.toString();
}

    final bytes = await file.readAsBytes();

    request.files.add(
      http.MultipartFile.fromBytes(
        'video',
        bytes,
        filename: file.name,
      ),
    );

    final streamedResponse = await request.send();

    final response = await http.Response.fromStream(
      streamedResponse,
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw AnalysisException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 200) {
      return AnalysisResult(
        assessmentId: body['assessment_id'],
        sessionId: body['session_id'],
        exercise: body['exercise'],
        fileName: file.name,
        status: body['status'],
        validReps: body['valid_reps'] ?? 0,
        measurement: body['measurement'],
        features: Map<String, dynamic>.from(
          body['features'] ?? {},
        ),
        quality: Map<String, dynamic>.from(
          body['quality'] ?? {},
        ),
      );
    }

    if (response.statusCode == 400) {
      throw AnalysisException(
        body['detail']?.toString() ??
            'The video could not be processed.',
      );
    }

    if (response.statusCode == 401) {
      throw AnalysisException(
        'Your session has expired. Please sign in again.',
      );
    }

    if (response.statusCode == 403) {
      throw AnalysisException(
        body['detail']?.toString() ??
            'You are not allowed to perform this assessment.',
      );
    }

    if (response.statusCode == 500) {
      throw AnalysisException(
        body['detail']?.toString() ??
            'Exercise processing failed.',
      );
    }

    throw AnalysisException(
      body['detail']?.toString() ??
          'Video analysis failed.',
    );
  } on AnalysisException {
    rethrow;
  } on http.ClientException {
    throw AnalysisException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw AnalysisException(
      'Something went wrong while uploading the video.',
    );
  }
}