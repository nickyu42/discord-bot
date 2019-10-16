import discord 
from discord.ext import commands
import random as rnd


GAME_RULES = """\
Rules:
    Each player gets 2 cards, your goal is to have the highest hand
    Playing each turn costs 10 credits, each new game you start off with 100
    When a game is started, i'll tell you when it's your turn
    you can either hit or stay by typing "hit" or "pass"

Usage:
    blackjack <command>

Commands:
    join       Join the game lobby
    exit       Leave the game lobby, leaving ingame doesn't mean you get your credits back
    start      Start a new game with all players in lobby
    stats      Get your game stats

Ingame Commands:
    hit 
    pass
"""


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


def convert_to_codeblock(string):
    """ 
    Method adds markdown syntax to keep the formatting intact 
    discord uses different formatting for messages
    so instead of a message we use a code block 
    Note: Temporary workaround
    """
    return '```\n' + string + '```\n'


def create_deck():
    """Creates a list of standard cards in a deck"""
    deck = []

    for type in 'SHDC':
        deck.append('A' + type)

        for n in range(2, 11):
            deck.append(str(n) + type)
        for r in 'JQK':
            deck.append(r + type)

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


class Player():

    def __init__(self, name, hand=None, author=None, sort='human'):
        self.name = name
        self.hand = hand
        self.sort = sort
        self.author = author


class Game():

    def __init__(self, players, bot):
        self.bot = bot
        self.deck = None

        # create a player object for each player
        self.players = [Player(p.name, author=p) for p in players]

        # add the dealer
        dealer = Player('dealer', sort='dealer')
        self.players.append(dealer)

        self.player_iterator = None
        self.current_player = None


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
        self.players[-1].hand = self.create_hand()

        self.player_iterator = iter(self.players)
        self.current_plr = next(self.player_iterator)

        dealer = get_dealer(self.players[-1])
        
        for player in self.players:
            if player.sort is not 'dealer':
                player.hand = self.create_hand()

                await self.bot.send_message(player.author, "A new game has started\nDealer's hand:\n" + dealer)
                await self.bot.send_message(player.author, "Your hand: \n" + get_cards(player))

                current_player_msg = "It's {} turn".format(self.current_plr.name)
                await self.bot.send_message(self.current_plr.author, current_player_msg)


    def get_highest_hand(self):
        """
        Method gets names of the players 
        with the highest hand value
    
        :return: list with player_names with the highest value
        """
        all_val = [calc_value(p.hand) for p in self.players]
        top_val = max(all_val)

        top_hands = []
        for player in self.players:
            if calc_value(player.hand) == top_val:
                top_hands.append(player)

        return top_hands


    async def end_turn(self):
        # keep adding cards while the dealer's hand value is less than 17
        while 0 < calc_value(self.current_plr.hand) < 17:
            self.current_plr.hand.append(self.take_card())

        winners = self.get_highest_hand()

        for player in self.players:
            if player.sort is not 'dealer':
                if player in winners:
                    banner = 'Congratz, you won!'
                else:
                    banner = 'Aww shucks, you lost\nBetter luck next time'

                dealer_hand = get_cards(self.current_plr)

                # generate message to send
                message_to_send = '\n'.join(["Dealer's hand: ", dealer_hand, banner])
                await self.bot.send_message(player.author, message_to_send)

        await self.start_turn()


    async def process_command(self, message):
        """
        Messages get parsed from the on_message event
        :param message: discord message object
        """

        cmd = message.content

        if cmd.lower() == 'hit':
            # add card to hand
            self.current_plr.hand.append(self.take_card())

            await self.bot.send_message(self.current_plr.author, get_cards(self.current_plr))


        elif cmd.lower() == 'pass':
            await self.bot.send_message(self.current_plr.author, 'You have passed')

            # move on to next player
            self.current_plr = next(self.player_iterator)

            if self.current_plr.sort == 'dealer':
                await self.end_turn()


class Blackjack():

    def __init__(self, bot):
        self.bot = bot
        self.ongoing_game = None

        # dict with all players waiting to play with discord id's
        self.lobby = []


    @commands.group(pass_context=True)
    async def blackjack(self, ctx):
        # if no subcommand is given, diplay game rules and instructions
        if ctx.invoked_subcommand is None:
            await self.bot.say(GAME_RULES)


    @blackjack.command(pass_context=True)
    async def join(self, ctx):
        author = ctx.message.author
        name = ctx.message.author.name

        if author not in self.lobby:
            self.lobby.append(author)
            await self.bot.say('{} has joined the game'.format(name))
        else:
            await self.bot.say("You're already in the lobby\nType <>blackjack exit to leave the lobby")
        

    @blackjack.command(pass_context=True)
    async def exit(self, ctx):
        author = ctx.message.author
        name = ctx.message.author.name

        if author in self.lobby:
            self.lobby.remove(author)
            await self.bot.send_message(author, "{} has left the lobby".format(name))

        # close game if lobby is empty
        if not self.lobby and self.ongoing_game: 
            del self.ongoing_game
            self.ongoing_game = None


    @blackjack.command()
    async def start(self):
        # only start if there is no ongoing game 
        # and lobby has atleast one player
        if self.ongoing_game or not self.lobby:
            return 

        self.ongoing_game = Game(self.lobby, self.bot)

        await self.ongoing_game.start_turn()


    async def on_message(self, message):
        """
        Method checks for messages when there is an ongoing game
        and parses them to the Game object 
        """
        if self.ongoing_game:
            await self.ongoing_game.process_command(message)


def setup(bot):
    bot.add_cog(Blackjack(bot))