import enum
from types import MemberDescriptorType

#Forum role thresholds
class ForumRoleThreshold(enum.Enum):
    JuniorThresh = 5
    MediorThresh = 7
    SeniorThresh = 9

class ForumRole(enum.Enum):
    Junior = 0
    Medior = 1
    Senior = 2


#Poll rate for forum scraping
DISCORD_BOT_FORUM_POLL_RATE_S = 10