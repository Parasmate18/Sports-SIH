import 'package:flutter/material.dart';

import 'theme/app_theme.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const AthletiqApp());
}

class AthletiqApp extends StatelessWidget {
  const AthletiqApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ATHLETIQ',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const LoginScreen(),
    );
  }
}
