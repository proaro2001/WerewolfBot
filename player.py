class Player:
    def __init__(self, user, role=None, seat=0, emo=None) -> None:
        """
        constructor

        :param user:    discord user, limited to one, cannot be changed once set
        :param role:    string of role representation, limited to one
        :param num:     int of seat number, limited to one
        :param emoji:   representation of user when vote is needed, limited to one
        """
        self.user   = user
        self.role   = role
        self.num    = seat
        self.emoji  = emo
    
    def getUser(self):
        """return the self.user"""
        return self.user
    
    def getName(self):
        """return the name of user in discord"""
        return self.user.name
    
    def getRole(self):
        """return the role for the player"""
        return self.role
    
    def getNum(self):
        """return the seat number of player"""
        return self.num
    
    def getEmoji(self):
        """return the emoji that represent the player"""
        return self.emoji
    
    
    def setRole(self, role):
        """assign role to player"""
        self.role = role
    
    def setNum(self, seat):
        """assign the seat number to player"""
        self.num = seat
    
    def setEmoji(self, emoji):
        """
        assign a emoji that represent the player
        The emoji usually change according to seat number
        especially for Werewolf game
        """
        self.emoji = emoji
