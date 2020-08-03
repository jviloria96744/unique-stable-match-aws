import json
import pytest
from sampling_function import unique_stable_match


unique_sm = {
    "workers": {
        "W1": ["F1", "F2", "F3"],
        "W2": ["F2", "F1", "F3"],
        "W3": ["F3", "F2", "F1"]
    },
    "firms": {
        "F1": ["W1", "W2", "W3"],
        "F2": ["W1", "W2", "W3"],
        "F3": ["W1", "W2", "W3"]
    }
}

unique_sm_match = {
    "W1": "F1",
    "W2": "F2",
    "W3": "F3",
    "F1": "W1",
    "F2": "W2",
    "F3": "W3",
}

non_unique_sm = {
    "workers": {
        "W1": ["F2", "F1", "F3"],
        "W2": ["F3", "F2", "F1"],
        "W3": ["F1", "F3", "F2"]
    },
    "firms": {
        "F1": ["W2", "W1", "W3"],
        "F2": ["W3", "W2", "W1"],
        "F3": ["W1", "W3", "W2"]
    }
}

non_unique_sm_match = {
    "W1": "F2",
    "W2": "F3",
    "W3": "F1",
    "F1": "W3",
    "F2": "W1",
    "F3": "W2",
}

test_cases = [
    (unique_sm, True),
    (non_unique_sm, False),
]
@pytest.mark.parametrize("body, expected", test_cases)
def test_has_stable_match(body, expected):

    assert unique_stable_match.has_unique_stable_match(body) == expected


test_cases = [
    (unique_sm, unique_sm_match),
    (non_unique_sm, non_unique_sm_match),
]
@pytest.mark.parametrize("body, expected", test_cases)
def test_gale_shapley(body, expected):

    assert unique_stable_match.gale_shapley(body) == expected
