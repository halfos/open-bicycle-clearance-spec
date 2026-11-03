from bikeclearance.fit import check_tyre


def test_tyre_fit_and_margin_class():
    profile = {
        "z_free_left": [[311, 30], [370, 30]],
        "z_free_right": [[311, 30], [370, 30]],
        "max_radius": 500,
    }
    assert check_tyre(profile, 622, 50, "road").status == "fit"
    assert check_tyre(profile, 622, 50, "all-road").status == "no-fit"


def test_fender_envelope_reduces_lateral_clearance():
    profile = {
        "z_free_left": [[311, 45], [380, 45]],
        "z_free_right": [[311, 45], [380, 45]],
        "max_radius": 500,
    }
    without_fender = check_tyre(profile, 622, 40)
    with_fender = check_tyre(profile, 622, 40, fender=True)
    assert with_fender.gap == without_fender.gap - 5


def test_profile_must_cover_the_reference_shape():
    profile = {
        "z_free_left": [[311, 80], [350, 80]],
        "z_free_right": [[311, 80], [350, 80]],
        "max_radius": 500,
    }
    assert check_tyre(profile, 622, 50).status == "insufficient data"
