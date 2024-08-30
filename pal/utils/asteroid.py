"""
    Contains the asteroid object and methods for propogation.
"""

class Asteroid:
    def __init__(self, mpc, ra, ra_rate, dec, dec_rate, mag, name=None):
        self.name = name
        self.mpc = mpc
        self.ra = ra
        self.ra_rate = ra_rate
        self.dec = dec
        self.dec_rate = dec_rate
        self.app_mag = mag

    def json(self):
        return {
            "name": self.name,
            "mpc": self.mpc,
            "ra": self.ra,
            "ra_rate": self.ra_rate,
            "dec": self.dec,
            "dec_rate": self.dec_rate,
            "app_mag": self.app_mag
        }
    
    def propogate(self, period):
        return None