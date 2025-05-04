"""
Gambling utilities for blackjack, slots, and roulette games
"""
import random
import asyncio
import logging
from enum import Enum, auto
from typing import List, Dict, Any, Tuple, Optional, Union
import discord
from discord.ui import View, Button, Select
from discord import ButtonStyle, SelectOption

logger = logging.getLogger(__name__)

class CardSuit(Enum):
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()
    SPADES = auto()

class Card:
    def __init__(self, suit: CardSuit, value: int):
        self.suit = suit
        self.value = value
    
    @property
    def display_value(self) -> str:
        if self.value == 1:
            return "A"
        elif self.value == 11:
            return "J"
        elif self.value == 12:
            return "Q"
        elif self.value == 13:
            return "K"
        else:
            return str(self.value)
    
    @property
    def blackjack_value(self) -> int:
        if self.value == 1:
            return 11  # Ace is 11 by default, can be 1 if needed
        elif self.value >= 10:
            return 10  # Face cards are worth 10
        else:
            return self.value
    
    @property
    def emoji(self) -> str:
        """Return the card emoji"""
        suits = {
            CardSuit.HEARTS: "♥️",
            CardSuit.DIAMONDS: "♦️",
            CardSuit.CLUBS: "♣️",
            CardSuit.SPADES: "♠️"
        }
        return f"{suits[self.suit]}{self.display_value}"

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """Reset the deck with all 52 cards"""
        self.cards = []
        for suit in CardSuit:
            for value in range(1, 14):
                self.cards.append(Card(suit, value))
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        """Deal a card from the deck"""
        if not self.cards:
            self.reset()
        return self.cards.pop()

class BlackjackGame:
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.deck = Deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.bet = 0
        self.result = ""
        self.message = None
    
    def start_game(self, bet: int):
        """Start a new game of blackjack"""
        self.bet = bet
        self.player_hand = [self.deck.deal(), self.deck.deal()]
        self.dealer_hand = [self.deck.deal(), self.deck.deal()]
        self.game_over = False
        self.result = ""
        return self.get_game_state()
    
    def get_game_state(self, reveal_dealer: bool = False) -> Dict[str, Any]:
        """Get the current game state"""
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        # Check if player has blackjack
        player_blackjack = len(self.player_hand) == 2 and player_value == 21
        dealer_blackjack = len(self.dealer_hand) == 2 and dealer_value == 21
        
        # Determine if game is over (natural blackjack)
        if player_blackjack or dealer_blackjack:
            self.game_over = True
            if player_blackjack and dealer_blackjack:
                self.result = "push"
            elif player_blackjack:
                self.result = "blackjack"
            elif dealer_blackjack:
                self.result = "dealer_blackjack"
        
        return {
            "player_hand": self.player_hand,
            "dealer_hand": self.dealer_hand if reveal_dealer else [self.dealer_hand[0]],
            "player_value": player_value,
            "dealer_value": dealer_value if reveal_dealer else self.dealer_hand[0].blackjack_value,
            "game_over": self.game_over,
            "result": self.result,
            "bet": self.bet,
            "reveal_dealer": reveal_dealer,
            "player_blackjack": player_blackjack,
            "dealer_blackjack": dealer_blackjack
        }
    
    def calculate_hand_value(self, hand: List[Card]) -> int:
        """Calculate the value of a hand, accounting for aces"""
        value = 0
        aces = 0
        
        for card in hand:
            if card.value == 1:  # Ace
                aces += 1
                value += 11
            else:
                value += card.blackjack_value
        
        # Adjust for aces if over 21
        while value > 21 and aces > 0:
            value -= 10  # Convert an ace from 11 to 1
            aces -= 1
        
        return value
    
    def hit(self) -> Dict[str, Any]:
        """Player takes another card"""
        if self.game_over:
            return self.get_game_state(True)
        
        self.player_hand.append(self.deck.deal())
        player_value = self.calculate_hand_value(self.player_hand)
        
        if player_value > 21:
            self.game_over = True
            self.result = "bust"
        
        return self.get_game_state()
    
    def stand(self) -> Dict[str, Any]:
        """Player stands, dealer plays"""
        if self.game_over:
            return self.get_game_state(True)
        
        self.game_over = True
        
        # Dealer draws until 17 or higher
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        while dealer_value < 17:
            self.dealer_hand.append(self.deck.deal())
            dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        player_value = self.calculate_hand_value(self.player_hand)
        
        if dealer_value > 21:
            self.result = "dealer_bust"
        elif dealer_value > player_value:
            self.result = "dealer_wins"
        elif dealer_value < player_value:
            self.result = "player_wins"
        else:
            self.result = "push"
        
        return self.get_game_state(True)
    
    def get_payout(self) -> int:
        """Calculate payout based on game result"""
        if self.result == "blackjack":
            return int(self.bet * 1.5)  # Blackjack pays 3:2
        elif self.result in ["player_wins", "dealer_bust"]:
            return self.bet  # Even money
        elif self.result == "push":
            return 0  # Return bet
        else:  # All losses
            return -self.bet

class BlackjackView(View):
    def __init__(self, game: BlackjackGame, economy):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.game = game
        self.economy = economy
        
    async def on_timeout(self):
        """Handle view timeout by disabling buttons"""
        self.disable_all_buttons()
        if self.game.message:
            try:
                embed = self.game.message.embeds[0]
                embed.add_field(name="Timeout", value="Game timed out due to inactivity.", inline=False)
                await self.game.message.edit(embed=embed, view=None)
            except Exception as e:
                logger.error(f"Error handling blackjack timeout: {e}")
    
    @discord.ui.button(label="Hit", style=ButtonStyle.primary)
    async def hit_button(self, interaction: discord.Interaction, button: Button):
        # Check if it's the player's game
        if str(interaction.user.id) != self.game.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        game_state = self.game.hit()
        embed = create_blackjack_embed(game_state)
        
        if game_state["game_over"]:
            self.disable_all_buttons()
            payout = self.game.get_payout()
            
            # Update player economy
            if payout > 0:
                await self.economy.add_currency(payout, "blackjack", {"game": "blackjack", "result": self.game.result})
                await self.economy.update_gambling_stats("blackjack", True, payout)
                embed.add_field(name="Payout", value=f"You won {payout} credits!", inline=False)
            elif payout < 0:
                await self.economy.update_gambling_stats("blackjack", False, abs(payout))
                embed.add_field(name="Loss", value=f"You lost {abs(payout)} credits.", inline=False)
            else:  # push
                embed.add_field(name="Push", value=f"Your bet of {self.game.bet} credits has been returned.", inline=False)
            
            new_balance = await self.economy.get_balance()
            embed.add_field(name="New Balance", value=f"{new_balance} credits", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self if not game_state["game_over"] else None)
    
    @discord.ui.button(label="Stand", style=ButtonStyle.secondary)
    async def stand_button(self, interaction: discord.Interaction, button: Button):
        # Check if it's the player's game
        if str(interaction.user.id) != self.game.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        game_state = self.game.stand()
        embed = create_blackjack_embed(game_state)
        
        self.disable_all_buttons()
        payout = self.game.get_payout()
        
        # Update player economy
        if payout > 0:
            await self.economy.add_currency(payout, "blackjack", {"game": "blackjack", "result": self.game.result})
            await self.economy.update_gambling_stats("blackjack", True, payout)
            embed.add_field(name="Payout", value=f"You won {payout} credits!", inline=False)
        elif payout < 0:
            await self.economy.update_gambling_stats("blackjack", False, abs(payout))
            embed.add_field(name="Loss", value=f"You lost {abs(payout)} credits.", inline=False)
        else:  # push
            embed.add_field(name="Push", value=f"Your bet of {self.game.bet} credits has been returned.", inline=False)
        
        new_balance = await self.economy.get_balance()
        embed.add_field(name="New Balance", value=f"{new_balance} credits", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

def create_blackjack_embed(game_state: Dict[str, Any]) -> discord.Embed:
    """Create an embed for a blackjack game"""
    embed = discord.Embed(
        title="Blackjack",
        description=f"Bet: {game_state['bet']} credits",
        color=discord.Color.green()
    )
    
    # Player hand
    player_cards = " ".join([card.emoji for card in game_state["player_hand"]])
    embed.add_field(
        name=f"Your Hand ({game_state['player_value']})",
        value=player_cards,
        inline=False
    )
    
    # Dealer hand
    dealer_cards = " ".join([card.emoji for card in game_state["dealer_hand"]])
    dealer_value = game_state["dealer_value"]
    
    if not game_state["reveal_dealer"]:
        dealer_name = f"Dealer's Hand (showing {dealer_value})"
    else:
        dealer_name = f"Dealer's Hand ({dealer_value})"
    
    embed.add_field(name=dealer_name, value=dealer_cards, inline=False)
    
    # Game result
    if game_state["game_over"]:
        result_text = ""
        if game_state["result"] == "blackjack":
            result_text = "Blackjack! You win!"
        elif game_state["result"] == "dealer_blackjack":
            result_text = "Dealer has Blackjack. You lose."
        elif game_state["result"] == "bust":
            result_text = "Bust! You went over 21."
        elif game_state["result"] == "dealer_bust":
            result_text = "Dealer busts! You win!"
        elif game_state["result"] == "player_wins":
            result_text = "You win!"
        elif game_state["result"] == "dealer_wins":
            result_text = "Dealer wins."
        elif game_state["result"] == "push":
            result_text = "Push! It's a tie."
        
        embed.add_field(name="Result", value=result_text, inline=False)
    
    return embed

class RouletteGame:
    """Roulette game implementation"""
    
    # Roulette wheel numbers (European style with single 0)
    WHEEL_NUMBERS = list(range(0, 37))  # 0-36
    
    # Number colors
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    # 0 is green
    
    # Bet types and payouts
    BET_TYPES = {
        "straight": {"description": "Single number", "payout": 35},
        "split": {"description": "Two adjacent numbers", "payout": 17},
        "street": {"description": "Three numbers in a row", "payout": 11},
        "corner": {"description": "Four numbers in a square", "payout": 8},
        "six_line": {"description": "Six numbers (two rows)", "payout": 5},
        "column": {"description": "12 numbers (a column)", "payout": 2},
        "dozen": {"description": "12 numbers (1-12, 13-24, 25-36)", "payout": 2},
        "red": {"description": "Red numbers", "payout": 1},
        "black": {"description": "Black numbers", "payout": 1},
        "even": {"description": "Even numbers", "payout": 1},
        "odd": {"description": "Odd numbers", "payout": 1},
        "low": {"description": "Low numbers (1-18)", "payout": 1},
        "high": {"description": "High numbers (19-36)", "payout": 1}
    }
    
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.message = None
        self.bet_amount = 0
        self.bet_type = None
        self.bet_value = None
        self.last_result = None
        self.history = []  # Last 10 spins
    
    def place_bet(self, amount: int, bet_type: str, bet_value: Any) -> bool:
        """Place a bet on the roulette table
        
        Args:
            amount: Bet amount
            bet_type: Type of bet (straight, red, black, etc.)
            bet_value: Value to bet on (number or None for color bets)
            
        Returns:
            True if bet was placed successfully, False otherwise
        """
        if bet_type not in self.BET_TYPES:
            return False
            
        self.bet_amount = amount
        self.bet_type = bet_type
        self.bet_value = bet_value
        return True
    
    def spin(self) -> Dict[str, Any]:
        """Spin the roulette wheel
        
        Returns:
            Result data dictionary
        """
        # Randomly select a number
        result = random.choice(self.WHEEL_NUMBERS)
        
        # Determine color
        if result == 0:
            color = "green"
        elif result in self.RED_NUMBERS:
            color = "red"
        else:
            color = "black"
            
        # Determine outcome
        won = False
        payout_multiplier = 0
        
        if self.bet_type == "straight":
            won = int(self.bet_value) == result
            payout_multiplier = self.BET_TYPES["straight"]["payout"]
        
        elif self.bet_type == "red":
            won = color == "red"
            payout_multiplier = self.BET_TYPES["red"]["payout"]
            
        elif self.bet_type == "black":
            won = color == "black"
            payout_multiplier = self.BET_TYPES["black"]["payout"]
            
        elif self.bet_type == "even":
            won = result != 0 and result % 2 == 0
            payout_multiplier = self.BET_TYPES["even"]["payout"]
            
        elif self.bet_type == "odd":
            won = result != 0 and result % 2 == 1
            payout_multiplier = self.BET_TYPES["odd"]["payout"]
            
        elif self.bet_type == "low":
            won = 1 <= result <= 18
            payout_multiplier = self.BET_TYPES["low"]["payout"]
            
        elif self.bet_type == "high":
            won = 19 <= result <= 36
            payout_multiplier = self.BET_TYPES["high"]["payout"]
            
        elif self.bet_type == "dozen":
            first_dozen = 1 <= result <= 12
            second_dozen = 13 <= result <= 24
            third_dozen = 25 <= result <= 36
            
            if self.bet_value == "1st" and first_dozen:
                won = True
            elif self.bet_value == "2nd" and second_dozen:
                won = True
            elif self.bet_value == "3rd" and third_dozen:
                won = True
                
            payout_multiplier = self.BET_TYPES["dozen"]["payout"]
            
        elif self.bet_type == "column":
            first_col = result % 3 == 1 and result != 0
            second_col = result % 3 == 2 and result != 0
            third_col = result % 3 == 0 and result != 0
            
            if self.bet_value == "1st" and first_col:
                won = True
            elif self.bet_value == "2nd" and second_col:
                won = True
            elif self.bet_value == "3rd" and third_col:
                won = True
                
            payout_multiplier = self.BET_TYPES["column"]["payout"]
        
        # Update history
        self.history.append(result)
        if len(self.history) > 10:
            self.history = self.history[-10:]
            
        # Calculate winnings
        winnings = 0
        if won:
            winnings = self.bet_amount * payout_multiplier
            
        # Create result
        self.last_result = {
            "number": result,
            "color": color,
            "won": won,
            "payout_multiplier": payout_multiplier,
            "winnings": winnings,
            "bet_amount": self.bet_amount,
            "bet_type": self.bet_type,
            "bet_value": self.bet_value,
            "net_gain": winnings if won else -self.bet_amount
        }
        
        return self.last_result

class RouletteView(View):
    """Interactive view for roulette game"""
    
    def __init__(self, player_id: str, economy, bet: int = 10):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.player_id = player_id
        self.economy = economy
        self.game = RouletteGame(player_id)
        self.bet = bet
        self.message = None
        self.add_bet_type_select()
        
    def add_bet_type_select(self):
        """Add the bet type selection dropdown"""
        options = [
            SelectOption(label="Red", value="red", description="Bet on red numbers", emoji="🔴"),
            SelectOption(label="Black", value="black", description="Bet on black numbers", emoji="⚫"),
            SelectOption(label="Even", value="even", description="Bet on even numbers", emoji="2️⃣"),
            SelectOption(label="Odd", value="odd", description="Bet on odd numbers", emoji="1️⃣"),
            SelectOption(label="Low (1-18)", value="low", description="Bet on numbers 1-18", emoji="⬇️"),
            SelectOption(label="High (19-36)", value="high", description="Bet on numbers 19-36", emoji="⬆️"),
            SelectOption(label="First Dozen (1-12)", value="dozen:1st", description="Bet on numbers 1-12", emoji="1️⃣"),
            SelectOption(label="Second Dozen (13-24)", value="dozen:2nd", description="Bet on numbers 13-24", emoji="2️⃣"),
            SelectOption(label="Third Dozen (25-36)", value="dozen:3rd", description="Bet on numbers 25-36", emoji="3️⃣"),
            SelectOption(label="Straight (Single Number)", value="straight", description="Bet on a single number", emoji="🎯")
        ]
        
        bet_select = Select(
            placeholder="Select bet type",
            options=options,
            custom_id="bet_type"
        )
        
        bet_select.callback = self.bet_type_selected
        self.add_item(bet_select)
        
    async def on_timeout(self):
        """Handle view timeout by disabling buttons"""
        self.disable_all_items()
        if self.message:
            try:
                embed = discord.Embed(
                    title="🎲 Roulette 🎲",
                    description="Game timed out due to inactivity.",
                    color=discord.Color.dark_gray()
                )
                balance = await self.economy.get_balance()
                embed.add_field(name="Your Balance", value=f"{balance} credits", inline=False)
                await self.message.edit(embed=embed, view=None)
            except Exception as e:
                logger.error(f"Error handling roulette timeout: {e}")
    
    async def bet_type_selected(self, interaction: discord.Interaction):
        """Handle bet type selection"""
        # Check if it's the player's game
        if str(interaction.user.id) != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
            
        value = interaction.data["values"][0]
        
        # Handle different bet types
        if ":" in value:
            bet_type, bet_value = value.split(":")
        else:
            bet_type = value
            bet_value = None
            
        # For straight bets, we need to show a number input modal
        if bet_type == "straight":
            await interaction.response.send_modal(
                RouletteNumberModal(self, self.bet)
            )
            return
            
        # Place the bet
        self.game.place_bet(self.bet, bet_type, bet_value)
        
        # Create and update embed
        embed = create_roulette_embed(self.game, bet_placed=True)
        self.disable_all_items()
        
        # Add spin button
        spin_button = Button(style=ButtonStyle.primary, label="Spin", custom_id="spin")
        spin_button.callback = self.spin_wheel
        self.add_item(spin_button)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def spin_wheel(self, interaction: discord.Interaction):
        """Handle spin button click"""
        # Check if it's the player's game
        if str(interaction.user.id) != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
            
        # Check if player has enough credits
        balance = await self.economy.get_balance()
        if balance < self.game.bet_amount:
            await interaction.response.send_message(
                f"You don't have enough credits! You need {self.game.bet_amount} credits to play.",
                ephemeral=True
            )
            return
            
        # Remove the bet amount
        await self.economy.remove_currency(self.game.bet_amount, "roulette_bet")
        
        # Spin the wheel
        result = self.game.spin()
        
        # Create embed with results
        embed = create_roulette_embed(self.game, spin_result=True)
        
        # Update player economy
        if result["won"]:
            await self.economy.add_currency(
                result["winnings"],
                "roulette_win",
                {"game": "roulette", "bet_type": self.game.bet_type}
            )
            await self.economy.update_gambling_stats("roulette", True, result["winnings"])
        else:
            await self.economy.update_gambling_stats("roulette", False, self.game.bet_amount)
            
        # Get new balance
        new_balance = await self.economy.get_balance()
        embed.add_field(name="New Balance", value=f"{new_balance} credits", inline=False)
        
        # Add play again button
        self.clear_items()
        play_again = Button(style=ButtonStyle.success, label="Play Again", custom_id="play_again")
        play_again.callback = self.play_again
        self.add_item(play_again)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def play_again(self, interaction: discord.Interaction):
        """Handle play again button click"""
        # Check if it's the player's game
        if str(interaction.user.id) != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
            
        # Reset game but keep history
        history = self.game.history
        self.game = RouletteGame(self.player_id)
        self.game.history = history
        
        # Clear and add items
        self.clear_items()
        self.add_bet_type_select()
        
        # Create embed
        embed = create_roulette_embed(self.game)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def disable_all_items(self):
        """Disable all buttons and selects"""
        for item in self.children:
            item.disabled = True

class RouletteNumberModal(discord.ui.Modal):
    """Modal for entering a number for straight bets"""
    
    def __init__(self, view: RouletteView, bet: int):
        super().__init__(title="Choose a Number (0-36)")
        self.view = view
        self.bet = bet
        
        # Add the input field
        self.number_input = discord.ui.TextInput(
            label="Enter a number between 0 and 36",
            placeholder="0-36",
            required=True,
            min_length=1,
            max_length=2
        )
        self.add_item(self.number_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission"""
        try:
            number = int(self.number_input.value)
            if 0 <= number <= 36:
                # Place the bet
                self.view.game.place_bet(self.bet, "straight", number)
                
                # Create and update embed
                embed = create_roulette_embed(self.view.game, bet_placed=True)
                self.view.disable_all_items()
                
                # Add spin button
                spin_button = Button(style=ButtonStyle.primary, label="Spin", custom_id="spin")
                spin_button.callback = self.view.spin_wheel
                self.view.add_item(spin_button)
                
                await interaction.response.edit_message(embed=embed, view=self.view)
            else:
                await interaction.response.send_message(
                    "Please enter a valid number between 0 and 36!",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid number!",
                ephemeral=True
            )

def create_roulette_embed(game: RouletteGame, bet_placed: bool = False, spin_result: bool = False) -> discord.Embed:
    """Create an embed for roulette game
    
    Args:
        game: Roulette game instance
        bet_placed: Whether a bet has been placed
        spin_result: Whether to show spin results
        
    Returns:
        Embed object
    """
    if spin_result and game.last_result:
        # Show spin results
        result = game.last_result
        
        # Determine color based on result
        if result["color"] == "red":
            embed_color = discord.Color.red()
            number_display = f"🔴 {result['number']}"
        elif result["color"] == "black":
            embed_color = discord.Color.dark_gray()
            number_display = f"⚫ {result['number']}"
        else:  # Green for 0
            embed_color = discord.Color.green()
            number_display = f"🟢 {result['number']}"
            
        embed = discord.Embed(
            title="🎲 Roulette Results 🎲",
            description=f"The ball lands on {number_display}!",
            color=embed_color
        )
        
        # Bet details
        bet_display = f"{result['bet_type'].title()}"
        if result['bet_value'] is not None:
            if result['bet_type'] == 'straight':
                bet_display += f" ({result['bet_value']})"
            else:
                bet_display += f" ({result['bet_value']})"
                
        embed.add_field(
            name="Your Bet",
            value=f"{bet_display}: {result['bet_amount']} credits",
            inline=False
        )
        
        # Win/loss info
        if result["won"]:
            win_text = f"🎉 You won {result['winnings']} credits! 🎉"
            win_text += f"\nPayout: {result['payout_multiplier']}:1"
            embed.add_field(name="Result", value=win_text, inline=False)
        else:
            embed.add_field(name="Result", value="❌ You lost your bet!", inline=False)
            
        # Show recent history
        if game.history:
            history_text = " ".join([f"{num}" for num in game.history])
            embed.add_field(name="Recent Numbers", value=history_text, inline=False)
            
    elif bet_placed:
        # Show bet confirmation
        embed = discord.Embed(
            title="🎲 Roulette 🎲",
            description="Your bet has been placed!",
            color=discord.Color.gold()
        )
        
        # Bet details
        bet_display = f"{game.bet_type.title()}"
        if game.bet_value is not None:
            if game.bet_type == 'straight':
                bet_display += f" ({game.bet_value})"
            else:
                bet_display += f" ({game.bet_value})"
                
        embed.add_field(
            name="Your Bet",
            value=f"{bet_display}: {game.bet_amount} credits",
            inline=False
        )
        
        embed.add_field(
            name="Ready?",
            value="Click 'Spin' to spin the wheel!",
            inline=False
        )
        
        # Show recent history
        if game.history:
            history_text = " ".join([f"{num}" for num in game.history])
            embed.add_field(name="Recent Numbers", value=history_text, inline=False)
            
    else:
        # Initial embed
        embed = discord.Embed(
            title="🎲 Roulette 🎲",
            description=f"Place your bet: {game.bet_amount} credits",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="How to Play",
            value="Select a bet type from the dropdown menu below.",
            inline=False
        )
        
        # Show recent history
        if game.history:
            history_text = " ".join([f"{num}" for num in game.history])
            embed.add_field(name="Recent Numbers", value=history_text, inline=False)
            
    return embed

class SlotMachine:
    def __init__(self):
        self.symbols = ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🎰"]
        self.weights = [20, 15, 15, 15, 10, 10, 10, 5]  # Weights for each symbol
        self.payouts = {
            "🍒": 2,   # Any 3 cherries
            "🍋": 3,   # Any 3 lemons
            "🍊": 4,   # Any 3 oranges
            "🍇": 5,   # Any 3 grapes
            "🍉": 8,   # Any 3 watermelons
            "💎": 10,  # Any 3 diamonds
            "7️⃣": 15,  # Any 3 sevens
            "🎰": 25   # Any 3 slot machines (jackpot)
        }
        self.special_combos = {
            ("7️⃣", "7️⃣", "7️⃣"): 20,  # Triple 7s (higher payout)
            ("🎰", "🎰", "🎰"): 50   # Triple slots (jackpot)
        }
    
    def spin(self) -> Tuple[List[str], int, int]:
        """Spin the slot machine and return results"""
        # Select symbols based on weights
        results = random.choices(self.symbols, weights=self.weights, k=3)
        
        # Check for special combinations
        tuple_result = tuple(results)
        if tuple_result in self.special_combos:
            multiplier = self.special_combos[tuple_result]
        # Check if all symbols are the same
        elif results[0] == results[1] == results[2]:
            multiplier = self.payouts[results[0]]
        # Check if two symbols are the same
        elif results[0] == results[1] or results[0] == results[2] or results[1] == results[2]:
            # Find the duplicated symbol
            if results[0] == results[1]:
                symbol = results[0]
            elif results[0] == results[2]:
                symbol = results[0]
            else:
                symbol = results[1]
            multiplier = self.payouts[symbol] // 2  # Half payout for two matching
        else:
            multiplier = 0
        
        return results, multiplier

class SlotsView(View):
    def __init__(self, player_id: str, economy, bet: int = 10):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.player_id = player_id
        self.economy = economy
        self.slot_machine = SlotMachine()
        self.bet = bet
        self.message = None
        
    async def on_timeout(self):
        """Handle view timeout by disabling buttons"""
        self.disable_all_buttons()
        if self.message:
            try:
                embed = discord.Embed(
                    title="🎰 Slot Machine 🎰",
                    description="Game timed out due to inactivity.",
                    color=discord.Color.dark_gray()
                )
                balance = await self.economy.get_balance()
                embed.add_field(name="Your Balance", value=f"{balance} credits", inline=False)
                await self.message.edit(embed=embed, view=None)
            except Exception as e:
                logger.error(f"Error handling slots timeout: {e}")
    
    @discord.ui.button(label="Spin", style=ButtonStyle.primary)
    async def spin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if it's the player's game
        if str(interaction.user.id) != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        # Check if player has enough credits
        balance = await self.economy.get_balance()
        if balance < self.bet:
            await interaction.response.send_message(f"You don't have enough credits! You need {self.bet} credits to play.", ephemeral=True)
            return
        
        # Remove the bet amount
        await self.economy.remove_currency(self.bet, "slots_bet")
        
        # Spin the slots
        symbols, multiplier = self.slot_machine.spin()
        
        # Calculate winnings
        winnings = self.bet * multiplier
        won = winnings > 0
        
        # Update player economy and gambling stats
        if won:
            await self.economy.add_currency(winnings, "slots_win", {"game": "slots", "multiplier": multiplier})
            await self.economy.update_gambling_stats("slots", True, winnings)
        else:
            await self.economy.update_gambling_stats("slots", False, self.bet)
        
        # Create the embed
        embed = discord.Embed(
            title="🎰 Slot Machine 🎰",
            description=f"Bet: {self.bet} credits",
            color=discord.Color.gold() if won else discord.Color.dark_gray()
        )
        
        # Add the spin animation effect with a loading message
        await interaction.response.defer()
        
        # Simulate spinning animation
        loading_embed = discord.Embed(
            title="🎰 Slot Machine 🎰",
            description="Spinning...",
            color=discord.Color.blue()
        )
        loading_embed.add_field(name="Bet", value=f"{self.bet} credits", inline=False)
        loading_message = await interaction.followup.send(embed=loading_embed)
        
        # Simulate spinning with random symbols
        for _ in range(3):
            temp_symbols = random.choices(self.slot_machine.symbols, k=3)
            temp_embed = discord.Embed(
                title="🎰 Slot Machine 🎰",
                description="Spinning...",
                color=discord.Color.blue()
            )
            temp_embed.add_field(name="Reels", value=" | ".join(temp_symbols), inline=False)
            await loading_message.edit(embed=temp_embed)
            await asyncio.sleep(0.7)
        
        # Show final result
        embed.add_field(name="Reels", value=" | ".join(symbols), inline=False)
        
        if won:
            embed.add_field(name="Result", value=f"🎉 You won {winnings} credits! 🎉", inline=False)
        else:
            embed.add_field(name="Result", value=f"Better luck next time!", inline=False)
        
        # Add new balance
        new_balance = await self.economy.get_balance()
        embed.add_field(name="Your Balance", value=f"{new_balance} credits", inline=False)
        
        # Update the message
        await loading_message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="Change Bet", style=ButtonStyle.secondary)
    async def change_bet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if it's the player's game
        if str(interaction.user.id) != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        # Create a modal for bet input
        modal = BetModal(title="Change Your Bet", current_bet=self.bet)
        await interaction.response.send_modal(modal)
        
        # Wait for the modal to be submitted
        timed_out = await modal.wait()
        
        if not timed_out and modal.value is not None:
            try:
                new_bet = int(modal.value)
                if new_bet <= 0:
                    await interaction.followup.send("Bet must be greater than 0!", ephemeral=True)
                else:
                    self.bet = new_bet
                    embed = discord.Embed(
                        title="🎰 Slot Machine 🎰",
                        description=f"Bet changed to {self.bet} credits",
                        color=discord.Color.blue()
                    )
                    
                    # Add current balance
                    balance = await self.economy.get_balance()
                    embed.add_field(name="Your Balance", value=f"{balance} credits", inline=False)
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
            except ValueError:
                await interaction.followup.send("Please enter a valid number!", ephemeral=True)
    
    @discord.ui.button(label="Quit", style=ButtonStyle.danger)
    async def quit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if it's the player's game
        if str(interaction.user.id) != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        self.disable_all_buttons()
        
        embed = discord.Embed(
            title="🎰 Slot Machine 🎰",
            description="Thanks for playing!",
            color=discord.Color.dark_gray()
        )
        
        # Add current balance
        balance = await self.economy.get_balance()
        embed.add_field(name="Your Balance", value=f"{balance} credits", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

class BetModal(discord.ui.Modal):
    def __init__(self, title: str, current_bet: int):
        super().__init__(title=title)
        self.value = None
        
        self.bet_input = discord.ui.TextInput(
            label="Enter your bet",
            placeholder=f"Current bet: {current_bet}",
            default=str(current_bet),
            required=True,
            min_length=1,
            max_length=6
        )
        self.add_item(self.bet_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.value = self.bet_input.value
        await interaction.response.defer()