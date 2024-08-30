
import ujson

class Config:
    DEFAULT_PATH: str = "config.ini"
    
    channels: list[str]
    channel: int
    squelch: int
    filter: int
    volume: int

    def __init__(self, path: str = DEFAULT_PATH):
        self.load(path)

    def load(self, path: str = DEFAULT_PATH):
        try:
            with open(Config.DEFAULT_PATH, "r") as f:
                dictionary = ujson.loads(f.read())
                for key, value in dictionary.items():
                    setattr(self, key, value)
                print("Loaded config:", self.__dict__)
        except OSError:
            # Default configuration
            self.channels = []
            for i in range(16):
                frequency = 446.00625 + (i * 0.0125)
                self.channels.append(f"{frequency:.4f}")
                self.channels.append(f"{frequency:.4f}")
            self.channel = 0
            self.squelch = 4
            self.filter = 0
            self.volume = 3
            print("Loaded default config:", self.__dict__)

    def save(self, path: str = DEFAULT_PATH):
        with open(path, "w") as f:
            f.write(ujson.dumps(self.__dict__))