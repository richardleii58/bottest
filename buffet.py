import uuid

class Buffet:
    # uuid = uuid.uuid4() # this generates a random string which acts as an ID
    def __init__(self, photo, location, expiry, diet, info): # when you create a buffet object, these are the variables that you need to give
        self.photo = photo # blob format?
        self.location = location
        self.expiry = expiry
        self.diet = diet
        self.info = info
