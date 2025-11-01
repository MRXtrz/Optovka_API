class ParserError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DatabaseError(ParserError):
    pass

class ScrapingError(ParserError):
    pass
