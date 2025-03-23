import enum

class Status(enum.Enum):
    confirmed = "confirmed"
    approved = "approved"
    checked_in = "checked_in"
    checked_out = "checked_out"
    under_maintenance = "under_maintenance"

class PaymentMethod(enum.Enum):
    card = "card"
    szep_card = "szep_card"
    cash = "cash"