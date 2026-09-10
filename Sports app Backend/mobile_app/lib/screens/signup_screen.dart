import 'package:flutter/material.dart';

import '../services/signup_service.dart';
import '../theme/app_colors.dart';
import '../widgets/error_banner.dart';
import '../widgets/loading_indicator.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>();

  String _role = 'ATHLETE';
  String _gender = 'M';
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _mobileController = TextEditingController();
  final _ageController = TextEditingController();
  final _addressController = TextEditingController();
  final _districtController = TextEditingController();
  final _postalController = TextEditingController();
  final _stateController = TextEditingController();
  final _countryController = TextEditingController(text: 'INDIA');
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _weightController = TextEditingController();
  final _heightController = TextEditingController();

  bool _loading = false;
  String _error = '';

  @override
  void dispose() {
    for (final c in [
      _firstNameController,
      _lastNameController,
      _mobileController,
      _ageController,
      _addressController,
      _districtController,
      _postalController,
      _stateController,
      _countryController,
      _usernameController,
      _passwordController,
      _weightController,
      _heightController,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  InputDecoration _decoration(String label) =>
      InputDecoration(labelText: label);

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = '';
    });
    try {
      final data = SignupData(
        role: _role,
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        mobileNo: _mobileController.text.trim(),
        age: int.parse(_ageController.text.trim()),
        gender: _gender,
        addressLine1: _addressController.text.trim(),
        district: _districtController.text.trim(),
        postalCode: _postalController.text.trim(),  
        state: _stateController.text.trim(),
        country: _countryController.text.trim().isEmpty
            ? 'INDIA'
            : _countryController.text.trim(),
        username: _usernameController.text.trim(),
        password: _passwordController.text,
        weight: _weightController.text.trim().isEmpty
            ? null
            : double.tryParse(_weightController.text.trim()),
        height: _heightController.text.trim().isEmpty
            ? null
            : double.tryParse(_heightController.text.trim()),
      );
      await signupUser(data);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Account created. Please sign in.')),
      );
      Navigator.of(context).pop();
    } on SignupException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgBase,
      appBar: AppBar(
        title: const Text(
          'Create Account',
          style: TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'I am a',
                  style: TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: RadioListTile<String>(
                        contentPadding: EdgeInsets.zero,
                        title: const Text(
                          'Athlete',
                          style: TextStyle(
                            color: AppColors.textPrimary,
                            fontSize: 13,
                          ),
                        ),
                        value: 'ATHLETE',
                        groupValue: _role,
                        activeColor: AppColors.accentPose,
                        onChanged: (v) => setState(() => _role = v!),
                      ),
                    ),
                    Expanded(
                      child: RadioListTile<String>(
                        contentPadding: EdgeInsets.zero,
                        title: const Text(
                          'Coach',
                          style: TextStyle(
                            color: AppColors.textPrimary,
                            fontSize: 13,
                          ),
                        ),
                        value: 'COACH',
                        groupValue: _role,
                        activeColor: AppColors.accentPose,
                        onChanged: (v) => setState(() => _role = v!),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _firstNameController,
                        decoration: _decoration('First Name'),
                        validator: (v) =>
                            (v == null || v.trim().isEmpty) ? 'Required' : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _lastNameController,
                        decoration: _decoration('Last Name'),
                        validator: (v) =>
                            (v == null || v.trim().isEmpty) ? 'Required' : null,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                TextFormField(
                  controller: _mobileController,
                  decoration: _decoration('Mobile Number'),
                  keyboardType: TextInputType.phone,
                  maxLength: 10,
                  validator: (v) => (v == null || v.trim().length != 10)
                      ? 'Enter 10-digit number'
                      : null,
                ),
                const SizedBox(height: 4),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _ageController,
                        decoration: _decoration('Age'),
                        keyboardType: TextInputType.number,
                        validator: (v) =>
                            (v == null || int.tryParse(v.trim()) == null)
                            ? 'Required'
                            : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: _gender,
                        decoration: _decoration('Gender'),
                        items: const [
                          DropdownMenuItem(value: 'M', child: Text('Male')),
                          DropdownMenuItem(value: 'F', child: Text('Female')),
                          DropdownMenuItem(value: 'O', child: Text('Other')),
                        ],
                        onChanged: (v) => setState(() => _gender = v!),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                const Text(
                  'Location (optional)',
                  style: TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _addressController,
                  decoration: _decoration('Address'),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _districtController,
                        decoration: _decoration('District'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _postalController,
                        decoration: _decoration('Postal Code'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _stateController,
                        decoration: _decoration('State'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _countryController,
                        decoration: _decoration('Country'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                const Text(
                  'Physical stats (optional)',
                  style: TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _weightController,
                        decoration: _decoration('Weight (kg)'),
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _heightController,
                        decoration: _decoration('Height (cm)'),
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                const Text(
                  'Account',
                  style: TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _usernameController,
                  decoration: _decoration('Username'),
                  validator: (v) => (v == null || v.trim().length < 4)
                      ? 'At least 4 characters'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  decoration: _decoration('Password'),
                  obscureText: true,
                  validator: (v) => (v == null || v.length <= 8)
                      ? 'At least 8 characters'
                      : null,
                ),
                const SizedBox(height: 20),

                if (_error.isNotEmpty) ...[
                  ErrorBanner(message: _error),
                  const SizedBox(height: 16),
                ],

                if (_loading)
                  const LoadingIndicator(message: 'Creating account…')
                else
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _submit,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.accentTrack,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text(
                        'Create Account',
                        style: TextStyle(
                          color: AppColors.textOnAccent,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
