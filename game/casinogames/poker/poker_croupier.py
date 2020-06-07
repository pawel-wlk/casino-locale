import itertools
from ..croupier import Croupier
from ..deck import Hand, Rank
from .winner_calc import convert, evaluate_hand, compare_hands

SMALL_BLIND = 1
BIG_BLIND = 2 * SMALL_BLIND


class PokerCroupier(Croupier):
    def __init__(self, *args):
        super().__init__(*args)
        self.round = 0
        self.bet = BIG_BLIND
        self.round_betted = False
        self.pot = 0

    def init_game(self):
        # blind bet
        self.pot += SMALL_BLIND
        self.players[0].balance -= SMALL_BLIND
        self.pot += BIG_BLIND
        self.players[1].balance -= BIG_BLIND

        for player in self.players:
            player.hand.cards = self.deck.get_cards(2)
            player.status = "first_round"
        self.players[2].his_turn = True
        self.status = "first_round"
        self.round = 1
        self.notify_all()

    def start_game(self):
        for player in self.players:
            player.his_turn = False
            player.status = "playing"
        self.table_cards.cards = self.deck.get_cards(3)
        self.players[0].his_turn = True
        self.status = "playing"
        self.round = 2
        self.notify_all()

    def notify_all(self):
        game_data = {
            "game_status": self.status,
            "game_round": self.round,
            "turn": [p.name for p in self.players if p.his_turn == True],
            "pot": self.pot,
            "bet": self.bet,
            "table_cards": self.table_cards.get_as_dict(),
            "round_betted": self.round_betted
        }
        for p in self.players:
            game_data["player"] = self.get_player_data(p)
            p.update(game_data)

    def notify_all_end(self):
        game_data = {
            "game_status": self.status,
            "game_round": self.round,
            "turn": [p.name for p in self.players if p.his_turn == True],
            "pot": self.pot,
            "bet": self.bet,
            "table_cards": self.table_cards.get_as_dict(),
            "round_betted": self.round_betted
        }
        game_data['players'] = [self.get_player_data(p) for p in self.players]
        for p in self.players:
            p.update(game_data)

    def get_player_data(self, player):
        if self.status != "finished":
            player.calc_available_moves()

        # nie mam pomysłu gdzie to zrobić, a tu to raczej być nie powinno xd
        if self.round == 1:
            if "bet" in player.available_moves:
                player.available_moves.remove("bet")
        elif self.round_betted:
            for move in ["bet", "check"]:
                if move in player.available_moves:
                    player.available_moves.remove(move)
        else:
            for move in ["raise", "call"]:
                if move in player.available_moves:
                    player.available_moves.remove(move)
            
        data = {
            "player": player.name,
            "hand": player.hand.get_as_dict(),
            "status": player.status,
            "balance": player.balance,
            "available_moves": player.available_moves,
        }
        return data

    def get_turn(self):
        for p in self.players:
            if p.his_turn:
                return p

    def next_turn(self):
        search_res = [i for i, p in enumerate(self.players) if p.his_turn]
        if len(search_res) == 0:
            for p in self.players:
                if p.status != "fold":
                    p.his_turn = True
                    return

        i = search_res[0]
        self.players[i].his_turn = False
        while self.players[(i+1) % len(self.players)].status == "fold":
            i+=1
        self.players[(i + 1) % len(self.players)].his_turn = True
        print(self.players[(i + 1) % len(self.players)].name)


    def next_turn_additional_round(self):
        search_res = [i for i, p in enumerate(self.players) if (p.status != "fold" and p.balance != -self.bet)]
        if len(search_res) == 0:
            return
        i = search_res[0]
        self.players[i].his_turn = True

    def last_player(self):
        for p in self.players[::-1]:
            if p.status != "fold":
                return p

    def process_move(self, channel_name, move):
        # If players are not ready, do nothing
        if not self.is_ready() or self.status == "finished":
            return


        i, p = [
            el for el in enumerate(self.players) if el[1].channel_name == channel_name
        ][0]
        # If it's not this player's turn, do nothing
        if not p.his_turn:
            print(f"{p.name}: not his turn")
            return

        def handle_move(player, move):
            print(f'{player.name} makes a move: {move["action"]}')

            if move["action"] == "fold":
                player.status = "fold"

            elif move["action"] == "bet":
                if type(move["value"]) != int:
                    return
                print(f'{player.name} bets {move["value"]}')
                self.round_betted = True
                self.pot += move["value"]
                self.bet += move["value"]
                player.balance -= move["value"]

            elif move["action"] == "call":
                if player.status == "additional_round":
                    self.pot += (player.balance + self.bet)
                    player.balance -= (player.balance + self.bet)
                elif player.status == "first_round":
                    self.pot += (player.balance + self.bet)
                    player.balance -= (player.balance + self.bet)
                    # if player.balance == -SMALL_BLIND:
                    #     self.pot += SMALL_BLIND
                    #     player.balance -= SMALL_BLIND
                    # else:
                    #     self.pot += BIG_BLIND
                    #     player.balance -= BIG_BLIND
                elif player.status == "playing":
                    if (
                        player == self.players[0]
                        or self.players[self.players.index(player) - 1].status
                        == "playing"
                    ):
                        # tutaj powinien wyrównywać do obecnej stawki cokolwiek to znaczy
                            # done - zakładając że player.balance w danej rozgrywce resetowany
                        self.pot += (player.balance + self.bet)
                        player.balance -= (player.balance + self.bet)

            elif move["action"] == "raise":
                if player.status == "first_round":
                    if type(move["value"]) != int:
                        return
                    print(f'{player.name} bets {move["value"]}')
                    self.pot += move["value"]
                    self.bet += move["value"]
                    player.balance = -self.bet
                elif (
                    player == self.players[0]
                    or self.players[self.players.index(player) - 1].status == "playing"
                ):
                    # wartość podbijania też powinna być jakoś sprawdzana
                    if type(move["value"]) != int:
                        return
                    print(f'{player.name} bets {move["value"]}')
                    self.pot += move["value"]
                    self.bet += move["value"]
                    player.balance = -self.bet

            elif move["action"] == "check":
                if (
                    player == self.players[0]
                    or self.players[self.players.index(player) - 1].status == "check"
                ):
                    player.status = "check"

            # self.notify_all()


            if self.round == 1 and not self.status == "additional_round":
                if self.players.index(player) == 0:
                    print("A")
                    if not all([(p.status == "fold" or -p.balance == self.bet) for p in self.players]):
                        self.status = "additional_round"
                        for p in [p for p in self.players if (p.status != "fold" and -p.balance != self.bet)]:
                            p.status = "additional_round"
                        for p in self.players:
                            p.his_turn = False
                        self.next_turn_additional_round()
                        self.notify_all()
                    else:
                        self.start_game()
                else:
                    print("B")
                    self.next_turn()
                    self.notify_all()
            elif not self.status == "additional_round" and self.round > 1 and self.round < 5:
                if player == self.last_player():
                    print("C")
                    if not all([(p.status == "fold" or -p.balance == self.bet) for p in self.players]):
                        self.status = "additional_round"
                        for p in [p for p in self.players if (p.status != "fold" and -p.balance != self.bet)]:
                            p.status = "additional_round"
                        for p in self.players:
                            p.his_turn = False
                        self.next_turn_additional_round()
                        self.notify_all()
                    else:
                        if self.round < 4:
                            self.round_betted = False
                            self.table_cards.add_cards(self.deck.get_cards(1))
                            for p in self.players:
                                if p.status != "fold":
                                    p.status = "playing"
                            self.status = "playing"
                            self.round += 1
                            self.next_turn()
                            self.notify_all()
                        else:
                            self.round += 1
                            self.notify_all()
                else:
                    print("D")
                    self.next_turn()
                    self.notify_all()
            elif self.status == "additional_round":
                if all([(p.status == "fold" or -p.balance == self.bet) for p in self.players]):
                    if self.round == 1:
                        self.start_game()
                    elif self.round < 4:
                        self.round_betted = False
                        self.table_cards.add_cards(self.deck.get_cards(1))
                        for p in self.players:
                            if p.status != "fold":
                                p.status = "playing"
                                p.his_turn = False
                        self.status = "playing"
                        self.round += 1
                        self.next_turn()
                        self.notify_all()
                    else:
                        self.round += 1
                        self.notify_all()
                else:
                    print("F")
                    self.next_turn_additional_round()
                    self.notify_all()
            else:
                print("XD")
            
            if len([p for p in self.players if p.status != "fold"]) == 1:
                won = [p for p in self.players if p.status != "fold"][0]
                print(f"Player {won.name} wons {self.pot}")
                self.status = "finished"
                return

            if self.round == 5: # and player == self.last_player():
                hands = []
                for p in self.players:
                    if p.status != "fold":
                        cards = convert(p.hand.cards) + convert(self.table_cards.cards)
                        best = 0
                        for possibility in list(map(list, list(itertools.combinations(cards, 5)))):
                            if evaluate_hand(possibility)[2] > best:
                                best, h = evaluate_hand(possibility)[2], possibility
                        hands.append((p, best, h))

                best = max(hands, key=lambda x: x[1])
                print(best)
                winners = [(p, c) for (p, v, c) in hands if v == best[1]]
                winner = winners[0]
                if len(winners) > 1:
                    for candidate in winners[1:]:
                        if compare_hands(winner[1], candidate[1])[0] == 'right':
                            winner = candidate
                winner[0].status = "won"
                winner[0].balance += self.pot
                print(f"Player {winner[0].name} has won {self.pot} with {winner[1]}")
                print("rozgrywka skończona")
                self.notify_all_end()
                return

                        
        handle_move(p, move)
