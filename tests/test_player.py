from game.card import Card, Color, CardType
from game.player import Player


def test_new_player_has_empty_hand():
    p = Player(name="Test")
    assert p.card_count() == 0


def test_add_cards_increases_hand():
    p = Player(name="Test")
    p.add_cards([Card(Color.RED, CardType.NUMBER, 1), Card(Color.BLUE, CardType.NUMBER, 2)])
    assert p.card_count() == 2


def test_remove_card_decreases_hand():
    p = Player(name="Test")
    card = Card(Color.RED, CardType.NUMBER, 1)
    p.add_cards([card])
    p.remove_card(card)
    assert p.card_count() == 0


def test_has_won_when_hand_empty_after_play():
    p = Player(name="Test")
    card = Card(Color.RED, CardType.NUMBER, 1)
    p.add_cards([card])
    p.remove_card(card)
    assert p.has_won() is True


def test_legal_moves_filters_correctly():
    p = Player(name="Test")
    p.add_cards([
        Card(Color.RED, CardType.NUMBER, 5),
        Card(Color.BLUE, CardType.NUMBER, 3),
        Card(Color.GREEN, CardType.NUMBER, 9),
    ])
    top = Card(Color.RED, CardType.NUMBER, 9)
    legal = p.legal_moves(top)
    assert len(legal) == 2
    assert Card(Color.BLUE, CardType.NUMBER, 3) not in legal


def test_clone_is_independent_of_original():
    p = Player(name="Test")
    card = Card(Color.RED, CardType.NUMBER, 5)
    p.add_cards([card])

    clone = p.clone()
    clone.remove_card(card)

    assert clone.card_count() == 0
    assert p.card_count() == 1  