class AttemptRecord {
  final String exercise;
  final String date;
  final int score;
  final String grade;
  const AttemptRecord({
    required this.exercise,
    required this.date,
    required this.score,
    required this.grade,
  });
}

const bool useMockHistory = true;

Future<List<AttemptRecord>> fetchAttemptHistory() async {
  if (useMockHistory) {
    await Future.delayed(const Duration(milliseconds: 600));
    return const [
      AttemptRecord(
        exercise: 'Vertical Jump',
        date: '2 Sept',
        score: 78,
        grade: 'B+',
      ),
      AttemptRecord(
        exercise: 'Shuttle Run',
        date: '30 Aug',
        score: 85,
        grade: 'A-',
      ),
      AttemptRecord(
        exercise: 'Sit-Ups',
        date: '28 Aug',
        score: 62,
        grade: 'C+',
      ),
      AttemptRecord(
        exercise: 'Sit and Reach',
        date: '25 Aug',
        score: 91,
        grade: 'A',
      ),
      AttemptRecord(
        exercise: 'Vertical Jump',
        date: '20 Aug',
        score: 70,
        grade: 'B',
      ),
    ];
  }
  // Real backend call goes here later, e.g. GET /api/history
  return [];
}
