import enum
from types import MemberDescriptorType

#Forum role thresholds
class ForumRoleThreshold(enum.IntEnum):
    Junior  = 100
    Medior  = 58
    Senior  = 500
    God     = 1000

class ForumRole(enum.IntEnum):
    Junior  = 0
    Medior  = 1
    Senior  = 2
    God     = 3


#Poll rate for forum scraping
DISCORD_BOT_FORUM_POLL_RATE_S = 10