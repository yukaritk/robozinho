class TransferRequest:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def start(self):
        print("[Transfer Request] Starting with login:", self.login)
        # Implement your logic here (e.g., Selenium browser control)
