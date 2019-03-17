import json
from hearthbreaker.agents.basic_agents import RandomAgent, GreedyAttackHeroAgent, GreedyControlHeroAgent
from hearthbreaker.cards.heroes import hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup
from hearthbreaker.cards import *
import timeit


def load_deck(filename):
    cards = []
    character_class = CHARACTER_CLASS.MAGE

    with open(filename, "r") as deck_file:
        contents = deck_file.read()
        items = contents.splitlines()
        for line in items[0:]:
            parts = line.split(" ", 1)
            count = int(parts[0])
            for i in range(0, count):
                card = card_lookup(parts[1])
                if card.character_class != CHARACTER_CLASS.ALL:
                    character_class = card.character_class
                cards.append(card)

    if len(cards) > 20:
        pass

    return Deck(cards, hero_for_class(character_class))


def do_stuff():
    _count = 0
    player_one_win = 0
    player_two_win = 0

    def play_game():
        nonlocal _count, player_two_win, player_one_win
        _count += 1
        new_game = game.copy()
        try:
            new_game.start()
        except Exception as e:
            print(json.dumps(new_game.__to_json__(), default=lambda o: o.__to_json__(), indent=1))
            print(new_game._all_cards_played)
            raise e

        print('Player one hp: ' + str(new_game.players[0].hero.health) + ' vs ' +
              'Player two hp: ' + str(new_game.players[1].hero.health))

        if new_game.players[1].hero.health == 0:
            player_one_win += 1
        else:
            player_two_win += 1

        del new_game

        if _count % 1000 == 0:
            print("---- game #{} ----".format(_count))

    deck1 = load_deck("test_deck.hsdeck")
    deck2 = load_deck("test_deck.hsdeck")
    game = Game([deck1, deck2], [GreedyAttackHeroAgent(), GreedyControlHeroAgent()])
    print('\nTime: ' + str(timeit.timeit(play_game, 'gc.enable()', number=1)))

    print('Player one won: ' + str(player_one_win) + ' games, '+ game.players[0].agent.__class__.__name__)
    print('Player two won: ' + str(player_two_win) + ' games, '+ game.players[1].agent.__class__.__name__)


if __name__ == "__main__":
    do_stuff()
