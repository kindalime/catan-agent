class BuildError(Exception):
    def __init__(self, object_id, owner_id, player_id, infra):
        self.message = f"Cannot build {infra} {object_id} for player {player_id} here: already owned by player {owner_id}!"
        super().__init__(self.message)

class TooCloseError(Exception):
    def __init__(self, object_id, player_id):
        self.message = f"Cannot build settlement {object_id} for player {player_id} here: too close to another settlement!"
        super().__init__(self.message)

class NotConnectedError(Exception):
    def __init__(self, object_id, player_id):
        self.message = f"Cannot build settlement {object_id} for player {player_id} here: not connected to a road!"
        super().__init__(self.message)

class BrokenRoadError(Exception):
    def __init__(self, object_id, player_id):
        self.message = f"Cannot build road {object_id} for player {player_id} here: not connected to a road!"
        super().__init__(self.message)

class UpgradeError(Exception):
    def __init__(self, object_id, owner):
        self.message = f"Cannot upgrade settlement {object_id} for player {owner} here: a city already exists!"
        super().__init__(self.message)

class NotEnoughResourcesError(Exception):
    def __init__(self, object_id, resource, need, own):
        self.message = f"Not enough resources for player {object_id}: need {need} {resource} but only have {own}!"
        super().__init__(self.message)

class OutOfCardsError(Exception):
    def __init__(self):
        self.message = f"Cannot draw a development card for player {player_id}, because the deck is empty!"
        super().__init__(self.message)

class DontHaveDevcardError(Exception):
    def __init__(self, player_id, card):
        self.message = f"Cannot play dev card of type {card} for player {player_id}, because player doesn't own that dev card!"
        super().__init__(self.message)

class CannotStealError(Exception):
    def __init__(self, player_id, victim_id, location):
        self.message = f"Cannot use the robber to steal from player {victim_id} to player {player_id} at location {location}!"
        super().__init__(self.message)

class DoNotDiscardError(Exception):
    def __init__(self, player_id):
        self.message = f"Player {player_id} does not have to discard cards due to not having more than 7 resources!"
        super().__init__(self.message)

class DiscardAmountWrongError(Exception):
    def __init__(self, player_id, discard, needed):
        self.message = f"Player {player_id} submitted the wrong number of resources to discard; submitted {discard} when they needed {needed}!"
        super().__init__(self.message)

class OutOfSettlementsError(Exception):
    def __init__(self, player_id):
        self.message = f"Player {player_id} cannot build a settlement because they are out of settlements!"
        super().__init__(self.message)
        
class OutOfCitiesError(Exception):
    def __init__(self, player_id):
        self.message = f"Player {player_id} cannot build a city because they are out of cities!"
        super().__init__(self.message)
