class NoDescriptionMoneycontrolException(Exception):
    """Useful for filtering earnings report which we get from alphastreet anyway. example: https://t.ly/Jd7PE"""

    def __init__(self, item):
        self.item = item
        self.message = "Moneycontrol item has no description"
        super().__init__(self.message, self.item)
