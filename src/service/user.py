class User:
    def __init__(self, user_data):
        self.user_data = user_data

    @property
    def user_id(self):
        return self.user_data.get('sub')

    @property
    def name(self):
        return self.user_data.get('nickname')

    @property
    def email(self):
        return self.user_data.get('email')