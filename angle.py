import numpy as np


def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    denominator = (
        np.linalg.norm(ba) *
        np.linalg.norm(bc)
    )

    if denominator == 0:
        return 0

    cosine_angle = np.dot(ba, bc) / denominator

    cosine_angle = np.clip(
        cosine_angle,
        -1.0,
        1.0
    )

    angle = np.degrees(
        np.arccos(cosine_angle)
    )

    return angle


# TEST
if __name__ == "__main__":

    a = (0, 1)
    b = (0, 0)
    c = (1, 0)

    angle = calculate_angle(a, b, c)

    print("Calculated Angle:", angle)