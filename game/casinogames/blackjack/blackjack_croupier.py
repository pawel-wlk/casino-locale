from ..croupier import Croupier
from ..deck import Hand, Rank

class BlackjackCroupier(Croupier):

    def __init__(self):
        super().__init__()
        self.hand = Hand()


    def init_game(self):
        for player in self.players:
            player.hand.cards = self.deck.get_cards(2)
            player.status = 'playing'
        self.hand.cards = self.deck.get_cards(1)
        self.notify_all()


    def notify_all(self):
        game_data = {'croupier': { 'hand': self.hand.get_as_dict(), 'sum': self.hand_sum(self.hand)}}
        game_data['players'] = [{'player': p.name, 'hand': p.hand.get_as_dict(), 'status': p.status, 'sum': self.hand_sum(p.hand)} for p in self.players]
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
        if i != self.counter or p.status != 'playing':
            print(f'{p.name}: not his turn')
            return

        if move == 'hit':
            p.hand.add_cards(self.deck.get_cards(1))
            if self.hand_sum(p.hand) > 21:
                p.status = 'lost'
                self.counter += 1
            elif self.hand_sum(p.hand) == 21:
                p.status = 'won'
                self.counter += 1
            
        elif move == 'stand':
            status = 'stand'
            self.counter += 1

        self.notify_all()

        # Croupier's turn
        if self.counter == len(self.players):
            while croupier_sum := self.hand_sum(self.hand) < 17:
                self.hand.add_cards(self.deck.get_cards(1))

            m = max(self.hand_sum(p.hand) for p in self.players if p.status != 'lost')

            if m > croupier_sum:
                best_players = [p for p in self.players if self.hand_sum(p.hand) == m]
                print(f'Winners: {[p.name for p in best_players]}')
            else:
                # Croupier won
                print('Croupier won')
                self.notify_all()

            print("KONIEC")
