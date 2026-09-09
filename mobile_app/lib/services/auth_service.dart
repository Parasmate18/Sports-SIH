import 'dart:convert';

import 'package:http/http.dart' as http;

class AuthResult {
  final String token;
  final String tokenType;
  final int userId;
  final String username;
  final String role;

  AuthResult({
    required this.token,
    required this.tokenType,
    required this.userId,
    required this.username,
    required this.role,
  });
}

class AuthException implements Exception {
  final String message;

  AuthException(this.message);
}

const String baseUrl = 'http://127.0.0.1:8000';

Future<AuthResult> loginUser(
  String username,
  String password,
) async {
  final cleanUsername = username.trim();

  if (cleanUsername.isEmpty || password.isEmpty) {
    throw AuthException('Enter both username and password.');
  }

  try {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/auth/login'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'username': cleanUsername,
        'password': password,
      }),
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw AuthException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 200) {
      return AuthResult(
        token: body['access_token'],
        tokenType: body['token_type'],
        userId: body['user_id'],
        username: body['username'],
        role: body['role'],
      );
    }

    if (response.statusCode == 401) {
      throw AuthException(
        body['detail'] ?? 'Invalid username or password.',
      );
    }

    throw AuthException(
      body['detail'] ?? 'Login failed.',
    );
  } on AuthException {
    rethrow;
  } on http.ClientException {
    throw AuthException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw AuthException(
      'Something went wrong while signing in.',
    );
  }
}