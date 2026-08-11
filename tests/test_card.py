import pytest

from game.card import Card, Color, CardType


def test_number_card_matches_same_color():
    c1 = Card(Color.RED, CardType.NUMBER, 7)
    top = Card(Color.RED, CardType.NUMBER, 3)
    assert c1.matches(top) is True


def test_number_card_matches_same_number_different_color():
    c1 = Card(Color.RED, CardType.NUMBER, 7)
    top = Card(Color.BLUE, CardType.NUMBER, 7)
    assert c1.matches(top) is True


def test_number_card_no_match_different_color_and_number():
    c1 = Card(Color.RED, CardType.NUMBER, 7)
    top = Card(Color.BLUE, CardType.NUMBER, 3)
    assert c1.matches(top) is False


def test_wild_always_matches_any_card():
    wild = Card(Color.WILD, CardType.WILD)
    top = Card(Color.GREEN, CardType.NUMBER, 5)
    assert wild.matches(top) is True


def test_wild_draw_four_always_matches():
    wild4 = Card(Color.WILD, CardType.WILD_DRAW_FOUR)
    top = Card(Color.YELLOW, CardType.SKIP)
    assert wild4.matches(top) is True


def test_special_card_matches_same_type_different_color():
    skip_red = Card(Color.RED, CardType.SKIP)
    skip_blue = Card(Color.BLUE, CardType.SKIP)
    assert skip_red.matches(skip_blue) is True


def test_special_card_no_match_different_type_and_color():
    skip_red = Card(Color.RED, CardType.SKIP)
    reverse_blue = Card(Color.BLUE, CardType.REVERSE)
    assert skip_red.matches(reverse_blue) is False


def test_active_color_overrides_top_card_color():
    # top_card je crvena, ali je boja "na snazi" (posle Wild karte) plava
    c_blue = Card(Color.BLUE, CardType.NUMBER, 4)
    top = Card(Color.RED, CardType.NUMBER, 9)
    assert c_blue.matches(top, active_color=Color.BLUE) is True
    assert c_blue.matches(top, active_color=Color.GREEN) is False


def test_card_is_immutable():
    c1 = Card(Color.RED, CardType.NUMBER, 7)
    with pytest.raises(Exception):
        c1.value = 9  # frozen dataclass mora da baci gresku


def test_is_wild_true_for_wild_types():
    assert Card(Color.WILD, CardType.WILD).is_wild() is True
    assert Card(Color.WILD, CardType.WILD_DRAW_FOUR).is_wild() is True


def test_is_wild_false_for_normal_card():
    assert Card(Color.RED, CardType.NUMBER, 5).is_wild() is False