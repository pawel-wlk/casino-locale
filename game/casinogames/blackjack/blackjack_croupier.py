from ..croupier import Croupier
from ..deck import Hand, Rank

class BlackjackCroupier(Croupier):

    def init_game(self):
        for player in self.players:
            player.status = 'betting'
        self.players[0].his_turn = True
        self.status = 'betting'
        self.notify_all()


    def start_game(self):
        for player in self.players:
            player.his_turn = False
            player.hand.cards = self.deck.get_cards(2)
            player.status = 'playing'
        self.table_cards.cards = self.deck.get_cards(1)
        self.players[0].his_turn = True
        self.status = 'playing'
        self.notify_all()


    def get_player_data(self, player):
        if self.status != 'finished':
            player.calc_available_moves()

        data = {
            'player': player.name,
            'hand': player.hand.get_as_dict(),
            'status': player.status,
            'sum': self.hand_sum(player.hand),
            'balance': player.balance,
            'available_moves': player.available_moves
        }
        return data


    def notify_all(self):
        game_data = {
            'croupier': { 
                'hand': self.table_cards.get_as_dict(), 
                'sum': self.hand_sum(self.table_cards)
            },
            'game_status': self.status,
            'pot': self.pot
        }
        game_data['players'] = [self.get_player_data(p) for p in self.players]
        for p in self.players:
            p.update(game_data)


    def hand_sum(self, hand):
        hand_sum = 0
        for card in hand.cards:
            if card.rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
                hand_sum += 10
            else:
                hand_sum += int(card.rank)
        return hand_sum


    # game_info idk how much should be sent
    def process_move(self, channel_name, move):
        # If players are not ready, do nothing
        if not self.is_ready():
            return

        i, p = [el for el in enumerate(self.players) if el[1].channel_name == channel_name][0]
        # If it's not this player's turn, do nothing
        if not p.his_turn:
            print(f'{p.name}: not his turn')
            return

        def handle_bet(player, move):
            if move['action'] == 'bet':
                print(f'{player.name} bets {move["value"]}')
                self.pot += move['value']
                player.balance -= move['value']
                self.next_turn()
            else:
                return

            if self.players.index(player) == len(self.players) - 1:
                self.start_game()


        def handle_move(player, move):
            print(f'{player.name} makes a move: {move["action"]}')
            if move['action'] == 'hit':
                player.hand.add_cards(self.deck.get_cards(1))
                if self.hand_sum(p.hand) > 21:
                    player.status = 'lost'
                    self.next_turn()
                elif self.hand_sum(p.hand) == 21:
                    player.status = 'won'
                    self.next_turn()

            elif move['action'] == 'stand':
                player.status = 'stand'
                self.next_turn()
            else:
                return

            self.notify_all()

            # Croupier's turn
            if self.players.index(player) == len(self.players) - 1:
                while croupier_sum := self.hand_sum(self.table_cards) < 17:
                    self.table_cards.add_cards(self.deck.get_cards(1))

                m = max(self.hand_sum(p.hand) for p in self.players if p.status != 'lost')
                if m > croupier_sum:
                    winners = [p for p in self.players if self.hand_sum(p.hand) == m]
                    print(f'Winners: {[p.name for p in winners]}')
                    for winner in winners:
                        winner.status = 'won'
                        winner.balance += int(self.pot / len(winners))
                self.status = 'finished'
                self.notify_all()
                print("KONIEC")

        if self.status == 'betting':
            handle_bet(p, move)
        elif self.status == 'playing':
            handle_move(p, move)
