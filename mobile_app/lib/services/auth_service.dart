class AuthResult {
  final String token;
  final String username;
  AuthResult({required this.token, required this.username});
}

class AuthException implements Exception {
  final String message;
  AuthException(this.message);
}

const bool useMock = true;

Future<AuthResult> loginUser(String username, String password) async {
  if (useMock) {
    await Future.delayed(const Duration(milliseconds: 900));
    if (username.isEmpty || password.isEmpty) {
      throw AuthException('Enter both username and password.');
    }
    if (password.length < 4) {
      throw AuthException('Invalid credentials. Try again.');
    }
    return AuthResult(
      token: 'mock-token-${DateTime.now().millisecondsSinceEpoch}',
      username: username,
    );
  }

  // Real backend call goes here later, e.g.:
  // final res = await http.post(Uri.parse('$baseUrl/api/auth/login'), ...);
  throw AuthException('Backend not connected yet.');
}
