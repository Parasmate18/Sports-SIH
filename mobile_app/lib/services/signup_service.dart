class SignupData {
  final String role;
  final String firstName;
  final String lastName;
  final String mobileNo;
  final int age;
  final String gender;
  final String? addressLine1;
  final String? district;
  final String? postalCode;
  final String? state;
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
    this.addressLine1,
    this.district,
    this.postalCode,
    this.state,
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

const bool useMockSignup = true;

Future<void> registerUser(SignupData data) async {
  if (useMockSignup) {
    await Future.delayed(const Duration(milliseconds: 900));
    if (data.username.length < 4) {
      throw SignupException('Username must be at least 4 characters.');
    }
    if (data.password.length < 6) {
      throw SignupException('Password must be at least 6 characters.');
    }
    if (data.mobileNo.length != 10) {
      throw SignupException('Enter a valid 10-digit mobile number.');
    }
    return; // success — mock accepts it
  }

  // Real backend call goes here later, e.g.:
  // POST /api/auth/register with `data` mapped to USER_DETAILS columns.
  throw SignupException('Backend not connected yet.');
}
