import discord 
from discord.ext import commands
import random as rnd

from .utils.formatting import convert_to_codeblock


CARD = """\
┌─────────┐
│{}       │
│         │
│         │
│    {}   │
│         │
│         │
│       {}│
└─────────┘
""".format('{rank: <2}', '{suit: <2}', '{rank: >2}')


HIDDEN_CARD = """\
┌─────────┐
│.........│
│.........│
│.........│
│.........│
│.........│
│.........│
│.........│
└─────────┘
"""


def join_lines(strings):
    """
    Stack strings horizontally
    :param strings: Strings to stack
    :return: String consisting of the horizontally stacked input
    """

    # two dimensional array containing each line of the string
    lines = [string.splitlines() for string in strings]

    # combine each line of the same index so they stack horizontally
    lines = [' '.join(lines) for lines in zip(*lines)]

    return '\n'.join(lines)


def ascii_version_of_card(cards):
    """
    Method to render an ASCII image of the card.
    :param cards: A list of text representation of cards
    :return: A string, the nice ascii version of cards
    """

    # we will use this to prints the appropriate icons for each card
    name_to_symbol = {
        'S': '♠',   # spades
        'D': '♦',   # diamonds
        'H': '♥',   # hearts
        'C': '♣'    # clubs
    }

    def card_to_string(card):
        # card format is (rank)(suite)
        suit = card[-1]
        rank = card[:-1]

        # add the individual card on a line by line basis
        return CARD.format(rank=rank, suit=name_to_symbol[suit])

    return join_lines(map(card_to_string, cards))


def ascii_version_of_hidden_card(cards):
    """
    Essentially the dealers method of print ascii cards. 
    This method hides the first card, shows it flipped over
    :param cards: A list of card objects, the first will be hidden
    :return: A string, the nice ascii version of cards
    """
    return join_lines((HIDDEN_CARD, ascii_version_of_card(cards[1:])))


def create_deck():
    """Creates a list of standard cards in a deck"""
    deck = []

    for suit in 'SHDC':
        deck.append('A' + suit)

        for n in range(2, 11):
            deck.append(str(n) + suit)
        for r in 'JQK':
            deck.append(r + suit)

    return deck


def calc_value(hand):
    """
    Method to calculate the value of the hand into an number
    returns 0 when the hand is bust, over 21
    :param hand: list of string ver of card
    :return: An int, the value of the hand
    """
    possible_hands = [0]

    # remove the suite 
    hand = [c[:-1] for c in hand]

    # convert royals to 10
    hand = [10 if c in "JQK" else c for c in hand]

    total_ace = hand.count("A")
    for a in range(total_ace + 1):
        temp_hand = []

        for card in hand:
            if card != "A":
                temp_hand.append(int(card))

        temp_hand.append(a * 11)
        temp_hand.append(total_ace - a)

        possible_hands.append(sum(temp_hand))

    # remove all possibilities which are over the value of 21
    possible_hands = filter(lambda x: x <= 21, possible_hands)

    return max(possible_hands)


def get_cards(player):
    """
    Method returns a page with the players cards and value
    :param player: Player object
    :return: string with stats
    """
    card_strings = ascii_version_of_card(player.hand)
    card_strings = convert_to_codeblock(card_strings)
    return card_strings 


def get_dealer(player):
    """
    Method returns a page with the players cards and value
    :param player: Player object
    :return: string with stats
    """
    card_strings = ascii_version_of_hidden_card(player.hand)
    card_strings = convert_to_codeblock(card_strings)
    return card_strings 


class Player:

    def __init__(self, name, author=None, hand=None):
        self.name = name
        self.author = author
        self.hand = hand


class Game:

    def __init__(self, player, bot):
        self.bot = bot
        self.deck = None
        self.is_done = False

        # create a player object 
        self.player = Player(player.name, author=player)

        # add the dealer
        self.dealer = Player('dealer')

    def create_hand(self):
        """Take 2 cards from the deck"""
        return [self.take_card() for _ in range(2)]

    def take_card(self):
        """Take a random card and remove it from the deck"""
        card = rnd.choice(self.deck)
        self.deck.remove(card)

        return card

    async def start_turn(self):
        # create new deck, and give the dealer 2 cards
        self.deck = create_deck()
        self.dealer.hand = self.create_hand()

        dealer = get_dealer(self.dealer)
        
        self.player.hand = self.create_hand()

        to_send = '\n'.join(["Dealer's hand:", 
                             dealer,
                             "Your hand:",
                             get_cards(self.player),
                             "Type 'hit' or 'pass' to continue.."])

        await self.bot.send_message(self.player.author, to_send)

    def get_highest_hand(self):
        """
        Method gets names of the players 
        with the highest hand value
    
        :return: string
        """
        dealer = calc_value(self.dealer.hand)
        player = calc_value(self.player.hand)

        if player == dealer:
            return "It's a draw"
        elif player > dealer:
            return "Congratz, you won!"
        else:
            return "Aww shucks, you lost\nBetter luck next time"

    async def end_turn(self):
        # keep adding cards while the dealer's hand value is less than 17
        while 0 < calc_value(self.dealer.hand) < 17:
            self.dealer.hand.append(self.take_card())

        result = self.get_highest_hand()
        dealer_hand = get_cards(self.dealer)
        hand_values = "Your hand had {} and dealer's hand had {}".format(calc_value(self.player.hand), 
                                                                         calc_value(self.dealer.hand))

        # generate message to send
        to_send = '\n'.join(["Dealer's hand: ", dealer_hand, result, hand_values])
        await self.bot.send_message(self.player.author, to_send)

        self.is_done = True

    async def process_command(self, message):
        """
        Messages get parsed from the on_message event
        :param message: discord message object
        """

        cmd = message.content

        if cmd.lower() == 'hit':
            # add card to hand
            self.player.hand.append(self.take_card())
            to_send = get_cards(self.player) + '\n' + "Type 'hit' or 'pass' to continue.."
            await self.bot.send_message(self.player.author, to_send)

        elif cmd.lower() == 'pass':
            await self.bot.send_message(self.player.author, 'You have passed')
            await self.end_turn()


class Blackjack:

    def __init__(self, bot):
        self.bot = bot
        self.ongoing_games = []

    @commands.group(pass_context=True, name='bj')
    async def blackjack(self, ctx):
        name = ctx.message.author.name

        # Don't start if the player is already in a game
        for game in self.ongoing_games:
            if name == game.player.name:
                await self.bot.say("You're already ingame")
                return

        self.ongoing_games.append(Game(ctx.message.author, self.bot))

        await self.ongoing_games[-1].start_turn()

    async def on_message(self, message):
        """
        Method checks for messages when there is an ongoing game
        and parses them to the Game object 
        """
        if self.ongoing_games:
            for game in self.ongoing_games:
                if not game.is_done:
                    await game.process_command(message)
                else:
                    # remove the game from the list if it's done
                    self.ongoing_games.remove(game)


def setup(bot):
    bot.add_cog(Blackjack(bot))