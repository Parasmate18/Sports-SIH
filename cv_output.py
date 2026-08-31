import json
from datetime import datetime


class CVOutput:

    def __init__(self, test_name):

        self.test_name = test_name
        self.frames = []
        self.valid_reps = 0
        self.invalid_reps = 0

    def add_frame_features(self, features):

        self.frames.append(features)

    def set_reps(self, valid_reps, invalid_reps=0):

        self.valid_reps = valid_reps
        self.invalid_reps = invalid_reps

    def generate(self):

        return {
            "test": self.test_name,

            "timestamp": datetime.now().isoformat(),

            "valid_reps": self.valid_reps,

            "invalid_reps": self.invalid_reps,

            "frame_features": self.frames
        }

    def save(self, filename="cv_result.json"):

        result = self.generate()

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        print()
        print("CV result saved:")
        print(filename)

        return result
