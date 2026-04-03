from dataclasses import dataclass

@dataclass
class Phrases:
    """Датакласс для фраз Алисы"""

    # формат хранения
    greeting: list = ("greeting1", "greeting2", "greeting3")
    success: list = ("success1", "success2", "success3")
