import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets(
    'basic Flutter app smoke test',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Text('ATHLETIQ'),
          ),
        ),
      );

      expect(
        find.text('ATHLETIQ'),
        findsOneWidget,
      );
    },
  );
}