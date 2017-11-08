class LsParseException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class LsEvalException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class LsGuiException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
