import 'dart:convert';

import 'package:http/http.dart' as http;

class SignupData {
  final String role;
  final String firstName;
  final String lastName;
  final String mobileNo;
  final int age;
  final String gender;

  final String addressLine1;
  final String district;
  final String postalCode;
  final String state;
  final String country;

  final String username;
  final String password;

  final double? weight;
  final double? height;

  SignupData({
    required this.role,
    required this.firstName,
    required this.lastName,
    required this.mobileNo,
    required this.age,
    required this.gender,
    required this.addressLine1,
    required this.district,
    required this.postalCode,
    required this.state,
    this.country = 'INDIA',
    required this.username,
    required this.password,
    this.weight,
    this.height,
  });
}

class SignupException implements Exception {
  final String message;

  SignupException(this.message);
}

const String baseUrl = 'http://172.16.239.150:8000';

String _normalizeRole(String role) {
  final value = role.trim().toUpperCase();

  if (value == 'ATHLETE' ||
      value == 'COACH' ||
      value == 'SCOUT') {
    return value;
  }

  throw SignupException('Invalid role selected.');
}

String _normalizeGender(String gender) {
  final value = gender.trim().toUpperCase();

  if (value == 'M' || value == 'MALE') {
    return 'M';
  }

  if (value == 'F' || value == 'FEMALE') {
    return 'F';
  }

  if (value == 'O' || value == 'OTHER') {
    return 'O';
  }

  throw SignupException('Invalid gender selected.');
}

Future<void> signupUser(SignupData data) async {
  if (data.firstName.trim().isEmpty ||
      data.lastName.trim().isEmpty ||
      data.username.trim().isEmpty ||
      data.password.isEmpty) {
    throw SignupException('Please fill all required fields.');
  }

  if (!RegExp(r'^\d{10}$').hasMatch(data.mobileNo.trim())) {
    throw SignupException(
      'Mobile number must contain exactly 10 digits.',
    );
  }

  if (data.postalCode.trim().isNotEmpty &&
      !RegExp(r'^\d{6}$').hasMatch(data.postalCode.trim())) {
    throw SignupException(
      'Postal code must contain exactly 6 digits.',
    );
  }

  if (data.password.length < 8) {
    throw SignupException(
      'Password must contain at least 8 characters.',
    );
  }

  try {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/auth/register'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'role': _normalizeRole(data.role),
        'first_name': data.firstName.trim(),
        'last_name': data.lastName.trim(),
        'mobile_number': data.mobileNo.trim(),
        'age': data.age,
        'gender': _normalizeGender(data.gender),

        'address_line_1':
            data.addressLine1.trim().isEmpty
                ? null
                : data.addressLine1.trim(),

        'district':
            data.district.trim().isEmpty
                ? null
                : data.district.trim(),

        'postal_code':
            data.postalCode.trim().isEmpty
                ? null
                : data.postalCode.trim(),

        'state':
            data.state.trim().isEmpty
                ? null
                : data.state.trim(),

        'country':
            data.country.trim().isEmpty
                ? 'INDIA'
                : data.country.trim(),

        'height_cm': data.height,
        'weight_kg': data.weight,

        'username': data.username.trim(),
        'password': data.password,
      }),
    );

    dynamic body;

    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw SignupException(
        'Invalid response received from the server.',
      );
    }

    if (response.statusCode == 201) {
      if (body['status'] == 'SUCCESS') {
        return;
      }

      throw SignupException(
        body['message'] ?? 'Registration failed.',
      );
    }

    if (response.statusCode == 400) {
      throw SignupException(
        body['detail'] ??
            'Registration could not be completed.',
      );
    }

    if (response.statusCode == 422) {
      throw SignupException(
        'Some registration details are invalid.',
      );
    }

    if (response.statusCode == 500) {
      throw SignupException(
        'Registration service is temporarily unavailable.',
      );
    }

    throw SignupException(
      body['detail'] ?? 'Registration failed.',
    );
  } on SignupException {
    rethrow;
  } on http.ClientException {
    throw SignupException(
      'Could not connect to backend server.',
    );
  } catch (_) {
    throw SignupException(
      'Something went wrong while creating your account.',
    );
  }
}