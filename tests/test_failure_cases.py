def test_no_person_detected():
    pose_landmarks = []

    if pose_landmarks:
        person_detected = True
    else:
        person_detected = False

    assert person_detected is False


def test_person_detected():
    pose_landmarks = [object()]

    if pose_landmarks:
        person_detected = True
    else:
        person_detected = False

    assert person_detected is True


if __name__ == "__main__":
    test_no_person_detected()
    test_person_detected()

    print("All failure-case tests passed!")