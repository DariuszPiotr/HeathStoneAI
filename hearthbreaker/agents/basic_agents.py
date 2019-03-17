import abc
import copy

import random
from hearthbreaker.cards.base import Card


class Agent(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def do_card_check(self, cards):
        pass

    @abc.abstractmethod
    def do_turn(self, player):
        pass

    @abc.abstractmethod
    def choose_target(self, targets):
        pass

    @abc.abstractmethod
    def choose_index(self, card, player):
        pass

    @abc.abstractmethod
    def choose_option(self, options, player):
        pass

    def filter_options(self, options, player):
        if isinstance(options[0], Card):
            return [option for option in options if option.can_choose(player)]
        return [option for option in options if option.card.can_choose(player)]


class DoNothingAgent(Agent):
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        pass

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


class PredictableAgent(Agent):
    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        done_something = True

        if player.hero.power.can_use():
            player.hero.power.use()

        if player.hero.can_attack():
            player.hero.attack()

        while done_something:
            done_something = False
            for card in player.hand:
                if card.can_use(player, player.game):
                    player.game.play_card(card)
                    done_something = True
                    break

        for minion in copy.copy(player.minions):
            if minion.can_attack():
                minion.attack()

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


class RandomAgent(DoNothingAgent):
    def __init__(self):
        super().__init__()

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        while True:
            attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
            if player.hero.can_attack():
                attack_minions.append(player.hero)
            playable_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
            if player.hero.power.can_use():
                possible_actions = len(attack_minions) + len(playable_cards) + 1
            else:
                possible_actions = len(attack_minions) + len(playable_cards)
            if possible_actions > 0:
                action = random.randint(0, possible_actions - 1)
                if player.hero.power.can_use() and action == possible_actions - 1:
                    player.hero.power.use()
                elif action < len(attack_minions):
                    attack_minions[action].attack()
                else:
                    player.game.play_card(playable_cards[action - len(attack_minions)])
            else:
                return

    def choose_target(self, targets):
        return targets[random.randint(0, len(targets) - 1)]

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]


class GreedyAttackHeroAgent(DoNothingAgent):
    def __init__(self):
        super().__init__()

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        while True:
            attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
            playable_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
            minions_cards = [card for card in filter(lambda card: card.is_minion(), player.hand)]
            temp = minions_cards[0].health
            possible_actions = len(attack_minions) + len(playable_cards)
            if possible_actions > 0:
                if len(attack_minions) > 0:
                    attack_minions[0].attack()
                else:
                    player.game.play_card(playable_cards[0])
            else:
                return

    def choose_target(self, targets, oponent_minions = [], attack = 0, health = 0):
        return targets[len(targets)-1]

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]
    

class GreedyControlHeroAgent(DoNothingAgent):
    def __init__(self):
        super().__init__()

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        while True:
            attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
            playable_cards = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
            possible_actions = len(attack_minions) + len(playable_cards)
            if possible_actions > 0:
                if len(attack_minions) > 0:
                    attack_minions[0].attack(player.opponent.minions)
                else:
                    player.game.play_card(playable_cards[0])
            else:
                return

    def choose_target(self, targets, oponent_minions = [], attack = 0, health = 0):
        if len(oponent_minions) == 0:
            return targets[len(targets)-1]
        my_attack = attack
        my_def = health

        index = self.find_best( (my_attack, my_def), oponent_minions )
        return targets[index]

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]
            
    def find_best(self, player, y):
        index = 0 
        total = -100
        idx_attack = 0
        idx_def = 0
        pl_attack = player[idx_attack]
        pl_deff = player[idx_def]
        
        for i in range(len(y)):
            attack = y[i].base_attack
            deff = y[i].health
            diff_attack = pl_attack - deff
            diff_deff = pl_deff - attack
            
            if diff_attack >= 0 and diff_deff > 0:
                total_temp = 50 + diff_attack + diff_deff
                if total_temp > total:
                    total = total_temp
                    index = i
                    print(f"{index},{total}")
            else:
                total_temp = diff_attack + diff_deff
                if total_temp > total:
                    total = total_temp
                    index = i
                    print(f"{index},{total}")
        
        return index

   