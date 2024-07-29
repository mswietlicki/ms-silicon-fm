class Config:
    DEFAULT_PATH: str = "config.ini"
    
    channels: list[str]
    channel: int
    squelch: int
    filter: int
    volume: int

    def __init__(self, dictionary = {}):
        for key, value in dictionary.items():
            setattr(self, key, value)