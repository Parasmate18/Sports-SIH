# SIH25073 — All 7 Real CV → M1 Integration

This package links the camera/CV assessment layer to the existing M1 talent model for the seven selected tests:

1. Push-up → `pushup_count`
2. Squat → `squat_count`
3. Deadlift → `deadlift_reps`
4. 50 m Running → `running_50m_seconds`
5. Sit-up → `situp_count`
6. Plank → `plank_duration_seconds`
7. Vertical Jump → `vertical_jump_cm`

The CV side writes each result to `cv_module/results/<test>.json` and also updates `cv_module/session_results.json`. M1 reads the session through `ml/cv_adapter.py`. A final prediction is allowed only after all seven required measurements plus age/gender/height/weight are available.

## Important accuracy limits

This is a hackathon prototype, not a certified sports-testing instrument. The new rep analyzers use multiple pose constraints and full movement state transitions, which reduces the false-positive problem in the original teammate code, but real-camera validation is still required on different athletes, camera angles, clothes, lighting, body sizes, and incorrect-form examples.

A single laptop camera cannot independently prove that someone ran exactly 50 metres. The Running test therefore requires a physically measured 50 m course and uses `S` / `F` for real elapsed timing while pose tracking checks that a person/movement is present. For a production system, replace this with synchronized start/finish cameras, timing gates, GPS/UWB, or another validated timing source.

Vertical-jump centimetres are estimated from a single-camera athlete-height calibration. Keep the whole body visible, keep the camera fixed, stand still during calibration, and validate the estimate against a measured reference before using it for official assessment.

Deadlift counting is not permission to perform unsupervised heavy lifting. Use only an age-appropriate, expert-approved standard load, correct equipment, and trained supervision.

## Windows setup

Open PowerShell in this folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If Windows Smart App Control blocks MediaPipe native libraries, that is an OS policy issue rather than a Python traceback caused by this repository. Do not weaken security settings just to run the project unless you understand the trade-off; a separate development environment or trusted/signed build is preferable.

## Test one exercise

```powershell
python -m cv_module.main
```

Menu:

```text
1. Push-up
2. Squat
3. Deadlift
4. 50 m Running
5. Sit-up
6. Plank
7. Vertical Jump
```

Press `Q` or `ESC` in the camera window to finish an exercise. For Running, press `S` to start and `F` at the 50 m finish.

## Run all seven and get the M1 prediction

```powershell
python run_full_assessment.py
```

The script asks for age, gender, height and weight, clears the previous CV session, runs all seven camera tests, then sends the resulting measurements directly to M1.

Flow:

```text
Real athlete
   ↓
Camera + MediaPipe Pose
   ↓
7 exercise analyzers
   ↓
cv_module/session_results.json
   ↓
ml/cv_adapter.py
   ↓
ml preprocessing + talent_model.pkl
   ↓
Talent-level prediction
```

## Run M1 from an already-completed CV session

Example:

```powershell
python -m ml.cv_adapter --session cv_module\session_results.json --age 17 --gender Male --height 172 --weight 62
```

No manual exercise values are needed when all seven CV results are complete.

## Why the new CV logic is stricter

The original Push-up code primarily counted elbow-angle threshold changes. That could count arm movement while standing. The new version also checks pose visibility, body alignment, horizontal push-up posture, and a complete down→up cycle. Squat, Sit-up, and Deadlift likewise use multiple joints/posture conditions. Invalid landmark geometry is rejected rather than treated as a legitimate `0°` measurement.

## Folder structure

```text
SIH25073_All7_CV_M1_Integrated/
├── cv_module/
│   ├── main.py
│   ├── pose_detector.py
│   ├── session_store.py
│   ├── pose_landmarker_lite.task
│   ├── session_results.json
│   ├── results/
│   ├── tests/
│   │   ├── pushup.py
│   │   ├── squat.py
│   │   ├── deadlift.py
│   │   ├── running.py
│   │   ├── situp.py
│   │   ├── plank.py
│   │   └── vertical_jump.py
│   └── utils/geometry.py
├── ml/
│   ├── cv_adapter.py
│   ├── cv_contract.json
│   ├── dataset.py
│   ├── preprocessing.py
│   ├── model.py
│   ├── train.py
│   ├── evaluate.py
│   ├── predict.py
│   └── saved_models/
├── run_full_assessment.py
├── requirements.txt
└── README.md
```

## Quick logic check (no camera)

```powershell
python -m cv_module.self_test
```

This verifies that standing arm movement is rejected as a push-up and that a complete synthetic push-up state cycle is counted. It is a code regression test only; it does not replace real-camera exercise testing.
