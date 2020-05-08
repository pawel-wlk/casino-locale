from ..croupier import Croupier

class BlackjackCroupier(Croupier):
    
    def results(self):
        pass

    # game_info idk how much should be sent
    def process_move(self, channel_name, move):
        for player in self.players:
            if player.channel_name == channel_name:
                p = player
                break
        if move == 'hit':
            card = self.deck.get_cards(1)[0]
            p.hand.append(card)
            if p.hand_sum() > 21: 
                p.update({'player': p.name, 'hand': p.hand, 'to': 'all', 'next': 'true'})
                self.counter += 1
            else:
                p.update({'player': p.name, 'hand': p.hand, 'to': 'all', 'next': 'false'})
        elif move == 'stand':
            p.update({'player': p.name, 'hand': p.hand, 'to': 'all', 'next': 'true'})
            self.counter += 1

        if self.counter == len(self.players):
            self.results()
            print("KONIEC")
