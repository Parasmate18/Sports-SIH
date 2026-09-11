import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/auth_service.dart';
import '../services/assessment_service.dart';
import '../services/analysis_service.dart';
import '../theme/app_colors.dart';
import '../widgets/error_banner.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/scan_frame.dart';
import 'dashboard_screen.dart';
import 'final_result_screen.dart';
import 'login_screen.dart';
import 'results_screen.dart';

enum UploadStatus { idle, loading, error }

class Exercise {
  final String id;
  final String label;

  const Exercise(this.id, this.label);
}

const exercises = [
  Exercise('pushup', 'Push-up'),
  Exercise('squat', 'Squat'),
  Exercise('deadlift', 'Deadlift'),
  Exercise('running', '50 m Running'),
  Exercise('situp', 'Sit-up'),
  Exercise('plank', 'Plank'),
  Exercise('vertical_jump', 'Vertical Jump'),
];

class _AthleteProfile {
  final int age;
  final String gender;
  final double heightCm;
  final double weightKg;

  const _AthleteProfile({
    required this.age,
    required this.gender,
    required this.heightCm,
    required this.weightKg,
  });
}

class UploadScreen extends StatefulWidget {
  final AuthResult auth;

  const UploadScreen({
    super.key,
    required this.auth,
  });

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String _exerciseId = exercises.first.id;

  XFile? _videoFile;
  int? _videoSizeBytes;

  UploadStatus _status = UploadStatus.idle;
  String _error = '';

  int? _assessmentId;

  bool _creatingAssessment = false;
  String _assessmentError = '';

  _AthleteProfile? _profile;

  final Map<String, AnalysisResult> _completedExercises = {};

  bool _finalizing = false;
  String _finalizeError = '';

  FinalAssessmentResult? _finalResult;

  bool _loadingSavedResult = false;
  String _savedResultError = '';

  final _profileFormKey = GlobalKey<FormState>();

  final _ageController = TextEditingController();
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();

  String _gender = 'Male';

  bool get _busy =>
      _creatingAssessment ||
      _status == UploadStatus.loading ||
      _finalizing ||
      _loadingSavedResult;

  bool get _allCompleted =>
      exercises.every(
        (exercise) => _completedExercises.containsKey(exercise.id),
      );

  @override
  void dispose() {
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();

    super.dispose();
  }

  // ==========================================================
  // ATHLETE PROFILE
  // ==========================================================

  void _submitProfile() {
    if (_busy || _profile != null) {
      return;
    }

    if (!_profileFormKey.currentState!.validate()) {
      return;
    }

    final profile = _AthleteProfile(
      age: int.parse(
        _ageController.text.trim(),
      ),
      gender: _gender,
      heightCm: double.parse(
        _heightController.text.trim(),
      ),
      weightKg: double.parse(
        _weightController.text.trim(),
      ),
    );

    setState(() {
      _profile = profile;
      _assessmentError = '';
    });

    _startAssessment();
  }

  // ==========================================================
  // CREATE ASSESSMENT
  // ==========================================================

  Future<void> _startAssessment() async {
    if (_profile == null ||
        _creatingAssessment ||
        _assessmentId != null) {
      return;
    }

    setState(() {
      _creatingAssessment = true;
      _assessmentError = '';
    });

    try {
      final session = await createAssessment(
        widget.auth.token,
      );

      if (!mounted) return;

      setState(() {
        _assessmentId = session.assessmentId;
        _creatingAssessment = false;
      });
    } on AssessmentException catch (e) {
      if (!mounted) return;

      setState(() {
        _creatingAssessment = false;
        _assessmentError = e.message;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _creatingAssessment = false;
        _assessmentError =
            'Could not start assessment.';
      });
    }
  }

  // ==========================================================
  // OPEN SAVED ASSESSMENT #43
  // ==========================================================

  Future<void> _openSavedResult() async {
    if (_busy) return;

    setState(() {
      _loadingSavedResult = true;
      _savedResultError = '';
    });

    try {
      final result = await getSavedAssessmentResult(
        assessmentId: 43,
        token: widget.auth.token,
      );

      if (!mounted) return;

      setState(() {
        _loadingSavedResult = false;
      });

      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => FinalResultScreen(
            result: result,
          ),
        ),
      );
    } on AssessmentException catch (e) {
      if (!mounted) return;

      setState(() {
        _loadingSavedResult = false;
        _savedResultError = e.message;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _loadingSavedResult = false;
        _savedResultError =
            'Could not load saved assessment result.';
      });
    }
  }

  // ==========================================================
  // EXERCISE MEASUREMENT KEY
  // ==========================================================

  String _measurementKeyForExercise(
    String exerciseId,
  ) {
    switch (exerciseId) {
      case 'pushup':
        return 'pushup_count';

      case 'squat':
        return 'squat_count';

      case 'deadlift':
        return 'deadlift_reps';

      case 'running':
        return 'running_50m_seconds';

      case 'situp':
        return 'situp_count';

      case 'plank':
        return 'plank_duration_seconds';

      case 'vertical_jump':
        return 'vertical_jump_cm';

      default:
        return '';
    }
  }

  // ==========================================================
  // VALIDATE EXERCISE RESULT
  // ==========================================================

  bool _isValidExerciseResult(
    AnalysisResult result,
  ) {
    if (result.status.toUpperCase() !=
        'SUCCESS') {
      return false;
    }

    if (result.measurement is! Map) {
      return false;
    }

    final measurement =
        Map<String, dynamic>.from(
      result.measurement as Map,
    );

    final expectedKey =
        _measurementKeyForExercise(
      result.exercise,
    );

    if (expectedKey.isEmpty) {
      return false;
    }

    final value =
        measurement[expectedKey];

    if (value is! num) {
      return false;
    }

    return value > 0 &&
        value.isFinite;
  }

  // ==========================================================
  // PICK VIDEO
  // ==========================================================

  Future<void> _pickVideo() async {
    if (_busy ||
        _assessmentId == null ||
        _finalResult != null) {
      return;
    }

    final source =
        await showModalBottomSheet<ImageSource>(
      context: context,
      backgroundColor:
          AppColors.bgSurface,
      shape:
          const RoundedRectangleBorder(
        borderRadius:
            BorderRadius.vertical(
          top: Radius.circular(16),
        ),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Column(
            mainAxisSize:
                MainAxisSize.min,
            children: [
              const SizedBox(
                height: 12,
              ),

              Container(
                width: 40,
                height: 4,
                decoration:
                    BoxDecoration(
                  color:
                      AppColors.borderSubtle,
                  borderRadius:
                      BorderRadius.circular(
                    2,
                  ),
                ),
              ),

              const SizedBox(
                height: 16,
              ),

              ListTile(
                leading: const Icon(
                  Icons.videocam,
                  color:
                      AppColors.accentPose,
                ),
                title: const Text(
                  'Record with camera',
                  style: TextStyle(
                    color:
                        AppColors.textPrimary,
                  ),
                ),
                onTap: () {
                  Navigator.of(ctx).pop(
                    ImageSource.camera,
                  );
                },
              ),

              ListTile(
                leading: const Icon(
                  Icons.photo_library,
                  color:
                      AppColors.accentPose,
                ),
                title: const Text(
                  'Choose from gallery',
                  style: TextStyle(
                    color:
                        AppColors.textPrimary,
                  ),
                ),
                onTap: () {
                  Navigator.of(ctx).pop(
                    ImageSource.gallery,
                  );
                },
              ),

              const SizedBox(
                height: 12,
              ),
            ],
          ),
        );
      },
    );

    if (source == null) {
      return;
    }

    try {
      final picker =
          ImagePicker();

      final picked =
          await picker.pickVideo(
        source: source,
        maxDuration:
            const Duration(
          minutes: 3,
        ),
      );

      if (picked == null) {
        return;
      }

      final size =
          await picked.length();

      if (!mounted) return;

      setState(() {
        _videoFile = picked;
        _videoSizeBytes = size;

        _status =
            UploadStatus.idle;

        _error = '';
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _status =
            UploadStatus.error;

        _error =
            'Could not select the video. Please try again.';
      });
    }
  }

  // ==========================================================
  // ANALYZE VIDEO
  // ==========================================================

  Future<void> _analyze() async {
    if (_busy ||
        _finalResult != null) {
      return;
    }

    if (_videoFile == null) {
      setState(() {
        _status =
            UploadStatus.error;

        _error =
            'Select a video before analyzing.';
      });

      return;
    }

    if (_assessmentId == null ||
        _profile == null) {
      setState(() {
        _status =
            UploadStatus.error;

        _error =
            'Assessment is not ready yet.';
      });

      return;
    }

    final selectedExercise =
        _exerciseId;

    final selectedFile =
        _videoFile!;

    final assessmentId =
        _assessmentId!;

    setState(() {
      _status =
          UploadStatus.loading;

      _error = '';

      _finalizeError = '';
    });

    try {
      final result =
          await analyzeVideo(
        file: selectedFile,
        exercise:
            selectedExercise,
        assessmentId:
            assessmentId,
        token:
            widget.auth.token,
        heightCm:
            _profile!.heightCm,
      );

      if (!mounted) return;

      setState(() {
        _status =
            UploadStatus.idle;

        if (_isValidExerciseResult(
          result,
        )) {
          _completedExercises[
              selectedExercise] = result;
        }

        _videoFile = null;

        _videoSizeBytes = null;
      });

      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) =>
              ResultsScreen(
            result: result,
          ),
        ),
      );
    } on AnalysisException catch (e) {
      if (!mounted) return;

      setState(() {
        _status =
            UploadStatus.error;

        _error = e.message;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _status =
            UploadStatus.error;

        _error =
            'Something went wrong while analyzing the video.';
      });
    }
  }

  // ==========================================================
  // FINALIZE ASSESSMENT
  // ==========================================================

  Future<void>
      _finalizeAssessment() async {
    if (_busy ||
        _assessmentId == null ||
        _profile == null ||
        !_allCompleted ||
        _finalResult != null) {
      return;
    }

    setState(() {
      _finalizing = true;
      _finalizeError = '';
    });

    try {
      final result =
          await finalizeAssessment(
        assessmentId:
            _assessmentId!,
        token:
            widget.auth.token,
        age:
            _profile!.age,
        gender:
            _profile!.gender,
        heightCm:
            _profile!.heightCm,
        weightKg:
            _profile!.weightKg,
      );

      if (!mounted) return;

      setState(() {
        _finalizing = false;
        _finalResult = result;
      });

      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) =>
              FinalResultScreen(
            result: result,
          ),
        ),
      );
    } on AssessmentException catch (e) {
      if (!mounted) return;

      setState(() {
        _finalizing = false;
        _finalizeError =
            e.message;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _finalizing = false;
        _finalizeError =
            'Could not finalize assessment.';
      });
    }
  }

  // ==========================================================
  // PROFILE INPUT FIELD
  // ==========================================================

  Widget _profileField({
    required String label,
    required TextEditingController
        controller,
    required String? Function(
      String?,
    ) validator,
    String? suffix,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType:
          const TextInputType
              .numberWithOptions(
        decimal: true,
      ),
      style: const TextStyle(
        color:
            AppColors.textPrimary,
      ),
      decoration:
          InputDecoration(
        labelText: label,
        suffixText: suffix,
        labelStyle:
            const TextStyle(
          color:
              AppColors.textMuted,
        ),
        filled: true,
        fillColor:
            AppColors.bgSurface,
        border:
            OutlineInputBorder(
          borderRadius:
              BorderRadius.circular(
            8,
          ),
        ),
      ),
      validator: validator,
    );
  }

  // ==========================================================
  // PROFILE FORM
  // ==========================================================

  Widget _buildProfileForm() {
    return Form(
      key: _profileFormKey,
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Text(
            'Athlete Profile',
            style: TextStyle(
              color:
                  AppColors.textPrimary,
              fontSize: 22,
              fontWeight:
                  FontWeight.w700,
            ),
          ),

          const SizedBox(
            height: 8,
          ),

          const Text(
            'Enter your measurements once before starting the assessment.',
            style: TextStyle(
              color:
                  AppColors.textMuted,
              fontSize: 13,
            ),
          ),

          const SizedBox(
            height: 24,
          ),

          _profileField(
            label: 'Age',
            controller:
                _ageController,
            validator: (value) {
              final age =
                  int.tryParse(
                value?.trim() ??
                    '',
              );

              if (age == null ||
                  age < 5 ||
                  age > 100) {
                return 'Enter an age between 5 and 100.';
              }

              return null;
            },
          ),

          const SizedBox(
            height: 16,
          ),

          DropdownButtonFormField<
              String>(
            value: _gender,
            dropdownColor:
                AppColors.bgSurface,
            style:
                const TextStyle(
              color:
                  AppColors.textPrimary,
            ),
            decoration:
                InputDecoration(
              labelText:
                  'Gender',
              labelStyle:
                  const TextStyle(
                color:
                    AppColors.textMuted,
              ),
              filled: true,
              fillColor:
                  AppColors.bgSurface,
              border:
                  OutlineInputBorder(
                borderRadius:
                    BorderRadius.circular(
                  8,
                ),
              ),
            ),
            items: const [
              DropdownMenuItem(
                value: 'Male',
                child: Text(
                  'Male',
                ),
              ),
              DropdownMenuItem(
                value: 'Female',
                child: Text(
                  'Female',
                ),
              ),
              DropdownMenuItem(
                value: 'Other',
                child: Text(
                  'Other',
                ),
              ),
            ],
            onChanged: (value) {
              if (value != null) {
                setState(() {
                  _gender = value;
                });
              }
            },
          ),

          const SizedBox(
            height: 16,
          ),

          _profileField(
            label: 'Height',
            controller:
                _heightController,
            suffix: 'cm',
            validator: (value) {
              final height =
                  double.tryParse(
                value?.trim() ??
                    '',
              );

              if (height ==
                      null ||
                  !height
                      .isFinite ||
                  height < 80 ||
                  height > 250) {
                return 'Enter height between 80 and 250 cm.';
              }

              return null;
            },
          ),

          const SizedBox(
            height: 16,
          ),

          _profileField(
            label: 'Weight',
            controller:
                _weightController,
            suffix: 'kg',
            validator: (value) {
              final weight =
                  double.tryParse(
                value?.trim() ??
                    '',
              );

              if (weight ==
                      null ||
                  !weight
                      .isFinite ||
                  weight < 20 ||
                  weight > 300) {
                return 'Enter weight between 20 and 300 kg.';
              }

              return null;
            },
          ),

          const SizedBox(
            height: 24,
          ),

          if (_creatingAssessment)
            const LoadingIndicator(
              message:
                  'Starting assessment…',
            )
          else
            SizedBox(
              width: double.infinity,
              child:
                  ElevatedButton(
                onPressed:
                    _submitProfile,
                style:
                    ElevatedButton
                        .styleFrom(
                  backgroundColor:
                      AppColors
                          .accentTrack,
                  padding:
                      const EdgeInsets
                          .symmetric(
                    vertical: 16,
                  ),
                  shape:
                      RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius
                            .circular(
                      8,
                    ),
                  ),
                ),
                child:
                    const Text(
                  'Start Assessment',
                  style: TextStyle(
                    color: AppColors
                        .textOnAccent,
                    fontWeight:
                        FontWeight
                            .w700,
                  ),
                ),
              ),
            ),

          if (_assessmentError
              .isNotEmpty) ...[
            const SizedBox(
              height: 16,
            ),
            ErrorBanner(
              message:
                  _assessmentError,
              onRetry:
                  _startAssessment,
            ),
          ],

          const SizedBox(
            height: 28,
          ),

          const Divider(
            color:
                AppColors.borderSubtle,
          ),

          const SizedBox(
            height: 20,
          ),

          const Text(
            'Previous Assessment',
            style: TextStyle(
              color:
                  AppColors.textPrimary,
              fontSize: 16,
              fontWeight:
                  FontWeight.w700,
            ),
          ),

          const SizedBox(
            height: 8,
          ),

          const Text(
            'Open your already-saved Assessment #43 result without uploading the videos again.',
            style: TextStyle(
              color:
                  AppColors.textMuted,
              fontSize: 12,
            ),
          ),

          const SizedBox(
            height: 14,
          ),

          if (_loadingSavedResult)
            const LoadingIndicator(
              message:
                  'Loading saved result…',
            )
          else
            SizedBox(
              width: double.infinity,
              child:
                  OutlinedButton.icon(
                onPressed:
                    _openSavedResult,
                icon:
                    const Icon(
                  Icons.history,
                  color: AppColors
                      .accentPose,
                ),
                label:
                    const Text(
                  'Open Assessment #43 Result',
                ),
                style:
                    OutlinedButton
                        .styleFrom(
                  foregroundColor:
                      AppColors
                          .textPrimary,
                  side:
                      const BorderSide(
                    color: AppColors
                        .borderSubtle,
                  ),
                  padding:
                      const EdgeInsets
                          .symmetric(
                    vertical: 16,
                  ),
                ),
              ),
            ),

          if (_savedResultError
              .isNotEmpty) ...[
            const SizedBox(
              height: 12,
            ),
            ErrorBanner(
              message:
                  _savedResultError,
              onRetry: () {
                setState(() {
                  _savedResultError =
                      '';
                });
              },
            ),
          ],
        ],
      ),
    );
  }

  // ==========================================================
  // PROGRESS
  // ==========================================================

  Widget _buildProgress() {
    final completedCount =
        _completedExercises.length;

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        const Text(
          'Assessment Progress',
          style: TextStyle(
            color:
                AppColors.textPrimary,
            fontSize: 16,
            fontWeight:
                FontWeight.w700,
          ),
        ),

        const SizedBox(
          height: 8,
        ),

        Text(
          '$completedCount / ${exercises.length} exercises completed',
          style: const TextStyle(
            color:
                AppColors.textMuted,
            fontSize: 13,
          ),
        ),

        const SizedBox(
          height: 12,
        ),

        LinearProgressIndicator(
          value:
              completedCount /
                  exercises.length,
          backgroundColor:
              AppColors.borderSubtle,
          color:
              AppColors.accentPose,
          minHeight: 6,
          borderRadius:
              BorderRadius.circular(
            4,
          ),
        ),

        const SizedBox(
          height: 16,
        ),

        Wrap(
          spacing: 8,
          runSpacing: 8,
          children:
              exercises.map(
            (exercise) {
              final completed =
                  _completedExercises
                      .containsKey(
                exercise.id,
              );

              return Chip(
                avatar: Icon(
                  completed
                      ? Icons
                          .check_circle
                      : Icons
                          .radio_button_unchecked,
                  size: 18,
                  color: completed
                      ? AppColors
                          .accentPose
                      : AppColors
                          .textMuted,
                ),
                label:
                    Text(
                  exercise.label,
                ),
                backgroundColor:
                    AppColors
                        .bgSurface,
                side:
                    const BorderSide(
                  color: AppColors
                      .borderSubtle,
                ),
                labelStyle:
                    const TextStyle(
                  color: AppColors
                      .textPrimary,
                  fontSize: 12,
                ),
              );
            },
          ).toList(),
        ),
      ],
    );
  }

  // ==========================================================
  // UPLOAD CONTENT
  // ==========================================================

  Widget _buildUploadContent() {
    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        const Text(
          'Submit your attempt',
          style: TextStyle(
            color:
                AppColors.textPrimary,
            fontSize: 22,
            fontWeight:
                FontWeight.w700,
          ),
        ),

        const SizedBox(
          height: 4,
        ),

        const Text(
          'Pick an exercise, upload a clear video, and let the AI analyze your performance.',
          style: TextStyle(
            color:
                AppColors.textMuted,
            fontSize: 13,
          ),
        ),

        const SizedBox(
          height: 16,
        ),

        Container(
          width: double.infinity,
          padding:
              const EdgeInsets.all(
            12,
          ),
          decoration:
              BoxDecoration(
            color:
                AppColors.bgSurface,
            borderRadius:
                BorderRadius.circular(
              8,
            ),
            border:
                Border.all(
              color:
                  AppColors.borderSubtle,
            ),
          ),
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment
                    .start,
            children: [
              Text(
                'Assessment #$_assessmentId ready',
                style:
                    const TextStyle(
                  color: AppColors
                      .textPrimary,
                  fontSize: 13,
                  fontWeight:
                      FontWeight
                          .w600,
                ),
              ),

              const SizedBox(
                height: 6,
              ),

              Text(
                'Age ${_profile!.age} • '
                '${_profile!.gender} • '
                '${_profile!.heightCm.toStringAsFixed(1)} cm • '
                '${_profile!.weightKg.toStringAsFixed(1)} kg',
                style:
                    const TextStyle(
                  color: AppColors
                      .textMuted,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),

        const SizedBox(
          height: 24,
        ),

        _buildProgress(),

        const SizedBox(
          height: 24,
        ),

        const Text(
          'EXERCISE',
          style: TextStyle(
            color:
                AppColors.textMuted,
            fontSize: 11,
            letterSpacing: 1.2,
          ),
        ),

        const SizedBox(
          height: 8,
        ),

        Container(
          decoration:
              BoxDecoration(
            color:
                AppColors.bgSurface,
            borderRadius:
                BorderRadius.circular(
              8,
            ),
            border:
                Border.all(
              color:
                  AppColors.borderSubtle,
            ),
          ),
          padding:
              const EdgeInsets
                  .symmetric(
            horizontal: 12,
          ),
          child:
              DropdownButtonHideUnderline(
            child:
                DropdownButton<
                    String>(
              value:
                  _exerciseId,
              isExpanded: true,
              dropdownColor:
                  AppColors
                      .bgSurface,
              style:
                  const TextStyle(
                color: AppColors
                    .textPrimary,
              ),
              onChanged:
                  _busy ||
                          _finalResult !=
                              null
                      ? null
                      : (value) {
                          if (value !=
                              null) {
                            setState(
                              () {
                                _exerciseId =
                                    value;

                                _videoFile =
                                    null;

                                _videoSizeBytes =
                                    null;

                                _error =
                                    '';

                                _status =
                                    UploadStatus
                                        .idle;
                              },
                            );
                          }
                        },
              items:
                  exercises.map(
                (exercise) {
                  return DropdownMenuItem(
                    value:
                        exercise.id,
                    child:
                        Text(
                      exercise.label,
                    ),
                  );
                },
              ).toList(),
            ),
          ),
        ),

        if (_completedExercises
                .containsKey(
              _exerciseId,
            ) &&
            _finalResult ==
                null) ...[
          const SizedBox(
            height: 8,
          ),
          const Text(
            'This exercise is already completed. Uploading again will create another attempt.',
            style: TextStyle(
              color:
                  AppColors.textMuted,
              fontSize: 12,
            ),
          ),
        ],

        const SizedBox(
          height: 24,
        ),

        ScanFrame(
          child:
              GestureDetector(
            onTap:
                _pickVideo,
            child: Container(
              width:
                  double.infinity,
              padding:
                  const EdgeInsets
                      .symmetric(
                vertical: 40,
                horizontal: 20,
              ),
              decoration:
                  BoxDecoration(
                color: AppColors
                    .bgSurface,
                borderRadius:
                    BorderRadius
                        .circular(
                  12,
                ),
                border:
                    Border.all(
                  color: AppColors
                      .borderSubtle,
                ),
              ),
              child:
                  const Column(
                children: [
                  Icon(
                    Icons
                        .videocam_outlined,
                    color: AppColors
                        .accentPose,
                    size: 32,
                  ),

                  SizedBox(
                    height: 12,
                  ),

                  Text(
                    'Tap to select your attempt video',
                    textAlign:
                        TextAlign
                            .center,
                    style:
                        TextStyle(
                      color: AppColors
                          .textPrimary,
                      fontWeight:
                          FontWeight
                              .w500,
                    ),
                  ),

                  SizedBox(
                    height: 4,
                  ),

                  Text(
                    'Camera or gallery',
                    style:
                        TextStyle(
                      color: AppColors
                          .textMuted,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),

        if (_videoFile !=
            null) ...[
          const SizedBox(
            height: 16,
          ),

          Container(
            padding:
                const EdgeInsets
                    .all(
              12,
            ),
            decoration:
                BoxDecoration(
              color: AppColors
                  .bgSurface,
              borderRadius:
                  BorderRadius
                      .circular(
                8,
              ),
              border:
                  Border.all(
                color: AppColors
                    .borderSubtle,
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child:
                      Column(
                    crossAxisAlignment:
                        CrossAxisAlignment
                            .start,
                    children: [
                      Text(
                        _videoFile!
                            .name,
                        style:
                            const TextStyle(
                          color: AppColors
                              .textPrimary,
                          fontSize:
                              13,
                        ),
                      ),

                      if (_videoSizeBytes !=
                          null)
                        Text(
                          '${(_videoSizeBytes! / (1024 * 1024)).toStringAsFixed(1)} MB',
                          style:
                              const TextStyle(
                            color:
                                AppColors
                                    .textMuted,
                            fontSize:
                                11,
                          ),
                        ),
                    ],
                  ),
                ),

                Container(
                  width: 8,
                  height: 8,
                  decoration:
                      const BoxDecoration(
                    color:
                        AppColors
                            .accentPose,
                    shape:
                        BoxShape
                            .circle,
                  ),
                ),
              ],
            ),
          ),
        ],

        const SizedBox(
          height: 20,
        ),

        if (_status ==
            UploadStatus.error)
          ErrorBanner(
            message: _error,
            onRetry: () {
              setState(() {
                _status =
                    UploadStatus.idle;
              });
            },
          ),

        if (_status ==
            UploadStatus.loading)
          const LoadingIndicator(
            message:
                'Uploading & analyzing…',
          )
        else
          SizedBox(
            width:
                double.infinity,
            child:
                ElevatedButton(
              onPressed:
                  _videoFile !=
                              null &&
                          _assessmentId !=
                              null &&
                          !_busy &&
                          _finalResult ==
                              null
                      ? _analyze
                      : null,
              style:
                  ElevatedButton
                      .styleFrom(
                backgroundColor:
                    AppColors
                        .accentTrack,
                disabledBackgroundColor:
                    AppColors
                        .accentTrack
                        .withOpacity(
                  0.3,
                ),
                padding:
                    const EdgeInsets
                        .symmetric(
                  vertical: 16,
                ),
                shape:
                    RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius
                          .circular(
                    8,
                  ),
                ),
              ),
              child:
                  const Text(
                'Analyze video',
                style:
                    TextStyle(
                  color: AppColors
                      .textOnAccent,
                  fontWeight:
                      FontWeight
                          .w700,
                ),
              ),
            ),
          ),

        if (_allCompleted) ...[
          const SizedBox(
            height: 20,
          ),

          if (_finalizeError
              .isNotEmpty) ...[
            ErrorBanner(
              message:
                  _finalizeError,
              onRetry: () {
                setState(() {
                  _finalizeError =
                      '';
                });
              },
            ),

            const SizedBox(
              height: 12,
            ),
          ],

          if (_finalizing)
            const LoadingIndicator(
              message:
                  'Finalizing assessment and running M1…',
            )
          else if (_finalResult ==
              null)
            SizedBox(
              width:
                  double.infinity,
              child:
                  ElevatedButton(
                onPressed:
                    _busy
                        ? null
                        : _finalizeAssessment,
                style:
                    ElevatedButton
                        .styleFrom(
                  backgroundColor:
                      AppColors
                          .accentPose,
                  padding:
                      const EdgeInsets
                          .symmetric(
                    vertical: 16,
                  ),
                  shape:
                      RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius
                            .circular(
                      8,
                    ),
                  ),
                ),
                child:
                    const Text(
                  'Finalize Assessment',
                  style:
                      TextStyle(
                    color: AppColors
                        .textOnAccent,
                    fontWeight:
                        FontWeight
                            .w700,
                  ),
                ),
              ),
            )
          else
            Container(
              width:
                  double.infinity,
              padding:
                  const EdgeInsets
                      .all(
                16,
              ),
              decoration:
                  BoxDecoration(
                color: AppColors
                    .bgSurface,
                borderRadius:
                    BorderRadius
                        .circular(
                  8,
                ),
                border:
                    Border.all(
                  color: AppColors
                      .accentPose,
                ),
              ),
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment
                        .start,
                children: [
                  const Text(
                    'Assessment Completed',
                    style:
                        TextStyle(
                      color: AppColors
                          .textPrimary,
                      fontSize: 16,
                      fontWeight:
                          FontWeight
                              .w700,
                    ),
                  ),

                  const SizedBox(
                    height: 8,
                  ),

                  Text(
                    'Status: ${_finalResult!.status}',
                    style:
                        const TextStyle(
                      color: AppColors
                          .textMuted,
                      fontSize: 13,
                    ),
                  ),

                  const SizedBox(
                    height: 4,
                  ),

                  Text(
                    'Talent Level: '
                    '${_finalResult!.prediction['talent_level'] ?? '-'}',
                    style:
                        const TextStyle(
                      color: AppColors
                          .textPrimary,
                      fontSize: 14,
                      fontWeight:
                          FontWeight
                              .w600,
                    ),
                  ),

                  const SizedBox(
                    height: 12,
                  ),

                  SizedBox(
                    width:
                        double.infinity,
                    child:
                        OutlinedButton(
                      onPressed: () {
                        Navigator.of(
                          context,
                        ).push(
                          MaterialPageRoute(
                            builder: (_) =>
                                FinalResultScreen(
                              result:
                                  _finalResult!,
                            ),
                          ),
                        );
                      },
                      child:
                          const Text(
                        'View Full Result',
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ],
    );
  }

  // ==========================================================
  // BUILD
  // ==========================================================

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      backgroundColor:
          AppColors.bgBase,
      appBar: AppBar(
        backgroundColor:
            AppColors.bgBase,
        elevation: 0,
        title: const Text(
          'ATHLETIQ',
          style: TextStyle(
            fontWeight:
                FontWeight.w700,
            letterSpacing: 1.1,
          ),
        ),
        actions: [
          IconButton(
            icon:
                const Icon(
              Icons.bar_chart,
              color:
                  AppColors.accentPose,
            ),
            onPressed:
                _busy
                    ? null
                    : () {
                        Navigator.of(
                          context,
                        ).push(
                          MaterialPageRoute(
                            builder: (_) =>
                                DashboardScreen(
                              username:
                                  widget.auth.username,
                                  token: widget.auth.token,
                            ),
                          ),
                        );
                      },
          ),
          IconButton(
             icon: const Icon(
             Icons.logout,
             color: AppColors.accentTrack,
               ),
              onPressed: _busy
              ? null
              : () {
             Navigator.of(context).pushAndRemoveUntil(
             MaterialPageRoute(
              builder: (_) => const LoginScreen(),
              ),
               (route) => false,
                );
                   },
          ),
        ],
      ),
      body: SafeArea(
        child:
            SingleChildScrollView(
          padding:
              const EdgeInsets.all(
            20,
          ),
          child:
              _profile == null ||
                      _assessmentId ==
                          null
                  ? _buildProfileForm()
                  : _buildUploadContent(),
        ),
      ),
    );
  }
}