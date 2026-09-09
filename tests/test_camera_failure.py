def check_camera(camera):
    if camera.isOpened():
        return True
    else:
        return False


class FakeCamera:
    def isOpened(self):
        return False


class WorkingCamera:
    def isOpened(self):
        return True


def test_camera_failure():
    camera = FakeCamera()

    result = check_camera(camera)

    assert result is False


def test_camera_success():
    camera = WorkingCamera()

    result = check_camera(camera)

    assert result is True


if __name__ == "__main__":
    test_camera_failure()
    test_camera_success()

    print("All camera failure tests passed!")