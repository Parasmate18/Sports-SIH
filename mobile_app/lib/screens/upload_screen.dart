import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/analysis_service.dart';
import '../theme/app_colors.dart';
import '../widgets/error_banner.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/scan_frame.dart';
import 'dashboard_screen.dart';
import 'results_screen.dart';

enum UploadStatus { idle, loading, error }

class Exercise {
  final String id;
  final String label;
  const Exercise(this.id, this.label);
}

const exercises = [
  Exercise('vertical_jump', 'Vertical Jump'),
  Exercise('shuttle_run', 'Shuttle Run'),
  Exercise('sit_ups', 'Sit-Ups'),
  Exercise('sit_and_reach', 'Sit and Reach'),
];

class UploadScreen extends StatefulWidget {
  final String username;
  const UploadScreen({super.key, required this.username});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String _exerciseId = exercises.first.id;
  XFile? _videoFile;
  int? _videoSizeBytes;
  UploadStatus _status = UploadStatus.idle;
  String _error = '';

  Future<void> _pickVideo() async {
    final source = await showModalBottomSheet<ImageSource>(
      context: context,
      backgroundColor: AppColors.bgSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppColors.borderSubtle,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.videocam, color: AppColors.accentPose),
              title: const Text(
                'Record with camera',
                style: TextStyle(color: AppColors.textPrimary),
              ),
              onTap: () => Navigator.of(ctx).pop(ImageSource.camera),
            ),
            ListTile(
              leading: const Icon(
                Icons.photo_library,
                color: AppColors.accentPose,
              ),
              title: const Text(
                'Choose from gallery',
                style: TextStyle(color: AppColors.textPrimary),
              ),
              onTap: () => Navigator.of(ctx).pop(ImageSource.gallery),
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );

    if (source == null) return;

    final picker = ImagePicker();
    final picked = await picker.pickVideo(
      source: source,
      maxDuration: const Duration(minutes: 3),
    );
    if (picked == null) return;
    final size = await picked.length();
    setState(() {
      _videoFile = picked;
      _videoSizeBytes = size;
      _status = UploadStatus.idle;
      _error = '';
    });
  }

  Future<void> _analyze() async {
    if (_videoFile == null) {
      setState(() {
        _status = UploadStatus.error;
        _error = 'Select a video before analyzing.';
      });
      return;
    }
    setState(() {
      _status = UploadStatus.loading;
      _error = '';
    });
    try {
      final result = await analyzeVideo(_videoFile!, _exerciseId);
      if (!mounted) return;
      setState(() => _status = UploadStatus.idle);
      Navigator.of(
        context,
      ).push(MaterialPageRoute(builder: (_) => ResultsScreen(result: result)));
    } on AnalysisException catch (e) {
      setState(() {
        _status = UploadStatus.error;
        _error = e.message;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgBase,
      appBar: AppBar(
        backgroundColor: AppColors.bgBase,
        elevation: 0,
        title: const Text(
          'ATHLETIQ',
          style: TextStyle(fontWeight: FontWeight.w700, letterSpacing: 1.1),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.bar_chart, color: AppColors.accentPose),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => DashboardScreen(username: widget.username),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: AppColors.accentTrack),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Submit your attempt',
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Pick an exercise, upload a clear video, and let the AI score your form.',
                style: TextStyle(color: AppColors.textMuted, fontSize: 13),
              ),
              const SizedBox(height: 24),

              const Text(
                'EXERCISE',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 11,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  color: AppColors.bgSurface,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _exerciseId,
                    isExpanded: true,
                    dropdownColor: AppColors.bgSurface,
                    style: const TextStyle(color: AppColors.textPrimary),
                    onChanged: (value) {
                      if (value != null) setState(() => _exerciseId = value);
                    },
                    items: exercises
                        .map(
                          (ex) => DropdownMenuItem(
                            value: ex.id,
                            child: Text(ex.label),
                          ),
                        )
                        .toList(),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              ScanFrame(
                child: GestureDetector(
                  onTap: _pickVideo,
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      vertical: 40,
                      horizontal: 20,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.borderSubtle),
                    ),
                    child: Column(
                      children: [
                        const Icon(
                          Icons.videocam_outlined,
                          color: AppColors.accentPose,
                          size: 32,
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Tap to select your attempt video',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Camera or gallery',
                          style: TextStyle(
                            color: AppColors.textMuted,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              if (_videoFile != null) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.bgSurface,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.borderSubtle),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _videoFile!.name,
                              style: const TextStyle(
                                color: AppColors.textPrimary,
                                fontSize: 13,
                              ),
                            ),
                            if (_videoSizeBytes != null)
                              Text(
                                '${(_videoSizeBytes! / (1024 * 1024)).toStringAsFixed(1)} MB',
                                style: const TextStyle(
                                  color: AppColors.textMuted,
                                  fontSize: 11,
                                ),
                              ),
                          ],
                        ),
                      ),
                      Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: AppColors.accentPose,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              const SizedBox(height: 20),

              if (_status == UploadStatus.error)
                ErrorBanner(
                  message: _error,
                  onRetry: () => setState(() => _status = UploadStatus.idle),
                ),

              if (_status == UploadStatus.loading)
                const LoadingIndicator(message: 'Uploading & analyzing…')
              else
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _videoFile != null ? _analyze : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.accentTrack,
                      disabledBackgroundColor: AppColors.accentTrack
                          .withOpacity(0.3),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      'Analyze video',
                      style: TextStyle(
                        color: AppColors.textOnAccent,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
