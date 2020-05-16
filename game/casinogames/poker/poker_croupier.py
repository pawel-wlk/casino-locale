from ..croupier import Croupier
from ..deck import Hand, Rank

SMALL_BLIND = 1
BIG_BLIND = 2 * SMALL_BLIND


class PokerCroupier(Croupier):
    def __init__(self):
        super().__init__()
        self.round = 0

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
            "table_cards": self.table_cards.get_as_dict(),
        }
        for p in self.players:
            game_data["player"] = self.get_player_data(p)
            p.update(game_data)

    def get_player_data(self, player):
        if self.status != "finished":
            player.calc_available_moves()

        data = {
            "player": player.name,
            "hand": player.hand.get_as_dict(),
            "status": player.status,
            "balance": player.balance,
            "available_moves": player.available_moves,
        }
        return data

    def process_move(self, channel_name, move):
        # If players are not ready, do nothing
        if not self.is_ready():
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
                self.next_turn()

            elif move["action"] == "bet":
                if type(move["value"]) != int:
                    return
                print(f'{player.name} bets {move["value"]}')
                self.pot += move["value"]
                player.balance -= move["value"]
                self.next_turn()

            elif move["action"] == "call":
                if player.status == "first_round":
                    self.pot += BIG_BLIND
                    player.balance -= BIG_BLIND
                    self.next_turn()
                if player.status == "playing":
                    if (
                        player == self.players[0]
                        or self.players[self.players.index(player) - 1].status
                        == "playing"
                    ):
                        # tutaj powinien wyrównywać do obecnej stawki cokolwiek to znaczy
                        self.pot += BIG_BLIND
                        player.balance -= BIG_BLIND
                        self.next_turn()

            elif move["action"] == "raise":
                if player.status == "first_round":
                    self.pot += 2 * BIG_BLIND
                    player.balance -= 2 * BIG_BLIND
                    self.next_turn()
                if (
                    player == self.players[0]
                    or self.players[self.players.index(player) - 1].status == "playing"
                ):
                    # wartość podbijania też powinna być jakoś sprawdzana
                    if type(move["value"]) != int:
                        return
                    print(f'{player.name} bets {move["value"]}')
                    self.pot += move["value"]
                    player.balance -= move["value"]
                    self.next_turn()

            elif move["action"] == "check":
                if (
                    player == self.players[0]
                    or self.players[self.players.index(player) - 1].status == "check"
                ):
                    player.status = "check"
                    self.next_turn()

            self.notify_all()

            if self.players.index(player) == len(self.players) - 1:
                if self.round == 1:
                    self.start_game()
                elif self.round < 5 and self.round > 1:
                    self.table_cards.add_cards(self.deck.get_cards(1))
                    for p in self.players:
                        p.status = "playing"
                    self.status = "playing"
                    self.round += 1
                    self.notify_all()
                elif self.round == 5:
                    pass

        handle_move(p, move)
