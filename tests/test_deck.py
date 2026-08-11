from game.deck import Deck


def test_deck_has_108_cards():
    d = Deck()
    assert d.cards_remaining() == 108


def test_draw_reduces_pile_size():
    d = Deck()
    d.draw(7)
    assert d.cards_remaining() == 101


def test_draw_returns_correct_number_of_cards():
    d = Deck()
    drawn = d.draw(5)
    assert len(drawn) == 5


def test_play_moves_card_to_discard_pile():
    d = Deck()
    card = d.draw(1)[0]
    d.play(card)
    assert d.top_card() == card
    assert len(d.discard_pile) == 1


def test_reshuffle_when_draw_pile_runs_out():
    d = Deck()
    all_but_two = d.draw(106)
    for c in all_but_two[:-1]:
        d.play(c)
    d.play(all_but_two[-1])
    drawn = d.draw(1)
    assert len(drawn) == 1


def test_clone_is_independent_of_original():
    d = Deck()
    original_count = d.cards_remaining()
    clone = d.clone()

    clone.draw(10)

    assert clone.cards_remaining() == original_count - 10
    assert d.cards_remaining() == original_count 