import enum
from types import MemberDescriptorType

#Forum role thresholds
class ForumRoleThreshold(enum.IntEnum):
    Junior = 2
    Medior = 4
    Senior = 6

class ForumRole(enum.IntEnum):
    Junior = 0
    Medior = 1
    Senior = 2


#Poll rate for forum scraping
DISCORD_BOT_FORUM_POLL_RATE_S = 10