import stock
import friends

class MTSAccount:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance
    
    @balance.setter
    def balance(self, new_balance):
        if new_balance >= 0:
            self._balance = new_balance
        else:
            raise ValueError("Balance must be non-negative")

def Create():
    '''Create an object and stage onto DB'''

'''>> helper function that loads a tuple from DB?'''

def Authenticate():
    '''TODO'''

def View():
    '''TODO'''

def Edit():
    '''TODO'''

def DailyBailout():
    '''TODO'''

def Delete():
    '''TODO'''