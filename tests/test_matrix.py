from bikeclearance.matrix import consistency, neighbouring_bsds, predict_matrix


def test_neighbouring_size_rule():
    assert neighbouring_bsds(622) == [597, 622, 630]
    assert neighbouring_bsds(406) == [355, 406, 451]


def test_prediction_and_consistency():
    record = {
        "level_a": {
            "matrices": {
                "without_fender": {"622": {"20": 60}},
                "with_fender": {},
            }
        },
        "level_b": {
            "profiles": {
                "622": {
                    "z_free_left": [[311, 50], [360, 50]],
                    "z_free_right": [[311, 50], [360, 50]],
                    "max_radius": 500,
                }
            }
        },
    }
    prediction = predict_matrix(record, widths=[20])
    assert prediction["without_fender"]["622"]["20"] == 40
    assert consistency(record)[0]["difference"] == 20
