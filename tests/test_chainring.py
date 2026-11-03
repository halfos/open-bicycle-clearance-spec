from bikeclearance.chainring import check_chainring


def test_chainring_fit_and_coverage():
    profile = [[35, 38], [60, 38], [110, 38], [120, 38]]
    result = check_chainring(profile, 50, 45)
    assert result.status == "fit"
    assert result.pitch_diameter == 202.3
    assert check_chainring([[35, 42], [120, 42]], 50, 45).status == "no-fit"
    assert check_chainring([[35, 38], [90, 38]], 50, 45).status == "insufficient data"
