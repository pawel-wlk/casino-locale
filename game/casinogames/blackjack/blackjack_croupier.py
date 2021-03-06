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
            'hand': [player.first_hand.get_as_dict(), player.second_hand.get_as_dict()],
            'status': player.status,
            'sum': self.hand_sum(player.hand),
            'balance': player.balance,
            'available_moves': player.available_moves,
            'splitted': player.splitted,
            'current_hand': player.hand_index
        }
        return data

    def notify_all(self, winners=[]):
        game_data = {
            'croupier': {
                'hand': self.table_cards.get_as_dict(),
                'sum': self.hand_sum(self.table_cards)
            },
            'game_status': self.status,
            'pot': self.pot,
            'winners': winners
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
        if hand_sum > 21 and Rank.ACE in [card.rank for card in hand.cards]:
            hand_sum -= 10
        return hand_sum

    def process_move(self, channel_name, move):
        # If players are not ready, do nothing
        if not self.is_ready():
            return

        i, p = [el for el in enumerate(
            self.players) if el[1].channel_name == channel_name][0]
        # If it's not this player's turn, do nothing
        if not p.his_turn:
            print(f'{p.name}: not his turn')
            return

        def handle_bet(player, move):
            if move['action'] == 'bet':
                if type(move["value"]) != int:
                    return
                print(f'{player.name} bets {move["value"]}')
                self.pot += move['value']
                print(player.balance)
                player.balance -= move['value']
                self.next_turn()
            else:
                return

            if self.players.index(player) == len(self.players) - 1:
                self.start_game()
            self.notify_all()

        def handle_move(player, move):
            print(f'{player.name} makes a move: {move["action"]}')

            if move['action'] == 'split':
                if 'split' in player.available_moves:
                    player.splitted = True
                    player.second_hand.cards = [player.first_hand.cards[1]]
                    player.first_hand.cards = [player.first_hand.cards[0]]
                else:
                    return

            elif move['action'] == 'double':
                if 'double' in player.available_moves:
                    player.doubled = True
                    self.pot -= player.balance
                    player.balance *= 2
                    player.hand.add_cards(self.deck.get_cards(1))
                    if self.hand_sum(p.hand) > 21:
                        player.status = 'lost'
                        self.next_turn()
                    else:
                        self.next_turn()
                else:
                    return

            elif player.splitted and move['action'] == 'hit':
                player.hand.add_cards(self.deck.get_cards(1))
                if self.hand_sum(p.hand) > 21:
                    if player.hand == player.first_hand:
                        player.hand = player.second_hand
                        player.hand_index = 1
                    else:
                        if self.hand_sum(player.first_hand) > 21:
                            player.status = 'lost'
                        else:
                            player.hand = player.first_hand
                        self.next_turn()

            elif move['action'] == 'hit':
                player.hand.add_cards(self.deck.get_cards(1))
                if self.hand_sum(p.hand) > 21:
                    player.status = 'lost'
                    self.next_turn()
                elif self.hand_sum(p.hand) == 21:
                    player.status = 'won'
                    self.next_turn()

            elif move['action'] == 'stand':
                if player.splitted and player.hand == player.first_hand:
                    player.hand = player.second_hand
                    player.hand_index = 1
                else:
                    if self.hand_sum(player.first_hand) < 21 and self.hand_sum(player.first_hand) > self.hand_sum(player.second_hand):
                        player.hand = player.first_hand
                        player.hand_index = 0
                    player.status = 'stand'
                    self.next_turn()
            else:
                return

            self.notify_all()

            # Croupier's turn
            if player.status != 'playing' and self.players.index(player) == len(self.players) - 1:
                while (croupier_sum := self.hand_sum(self.table_cards)) < 17:
                    self.table_cards.add_cards(self.deck.get_cards(1))

                print('dealer sum', croupier_sum)
                winners = [p for p in self.players if (p.status != 'lost' and (self.hand_sum(
                    p.hand) > croupier_sum or croupier_sum > 21)) or p.status == 'won']
                print(f'Winners: {[p.name for p in winners]}')
                for winner in winners:
                    winner.status = 'won'
                    winner.balance += int(self.pot / len(winners))

                self.status = 'finished'
                self.notify_all([p.name for p in winners])
                print("KONIEC")

        if self.status == 'betting':
            handle_bet(p, move)
        elif self.status == 'playing':
            handle_move(p, move)
