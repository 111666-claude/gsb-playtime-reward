"""在线时长档位奖励：按真实时间累计在线时长、档位达标领取、跨服务日刷新。

缺陷：同刻重复推进会重复累计、推进时间回退照收、达标用大于、领取不幂等、
没有每日领取配额、跨服务日不刷新、一次跨多档只认最后一个、每次查询全扫玩家表。
"""

MINUTE_MS = 60000


class Rewards:
    """在线时长奖励台账。"""

    def __init__(self, tiers, max_claims=2):
        self.tiers = list(tiers)
        self.max_claims = max_claims
        self.players = {}
        self.scanned = 0

    def _state(self, player):
        state = self.players.get(player)
        if state is None:
            state = {"last": 0, "played": 0, "claimed": set(), "day": 1, "claims": 0}
            self.players[player] = state
        return state

    def tick(self, player, now_ms, online):
        """推进在线时长。缺陷：不推进 last、时间回退也照收。"""
        state = self._state(player)
        state["played"] += now_ms - state["last"]
        return True

    def played_ms(self, player):
        """累计在线毫秒。缺陷：每次全扫玩家表。"""
        self.scanned += len(self.players)
        return self._state(player)["played"]

    def claimable(self, player):
        """可领档位下标。缺陷：达标用大于、只认最后一个达标档位、全扫玩家表。"""
        self.scanned += len(self.players)
        minutes = self._state(player)["played"] // MINUTE_MS
        last = -1
        for index, (need, _) in enumerate(self.tiers):
            if minutes > need:
                last = index
        if last < 0:
            return []
        return [last]

    def claim(self, player, tier):
        """领取档位。缺陷：不幂等、不看每日领取配额。"""
        self._state(player)["claimed"].add(tier)
        return True

    def claimed(self, player):
        """已领档位。缺陷：每次全扫玩家表。"""
        self.scanned += len(self.players)
        return sorted(self._state(player)["claimed"])

    def reset_day(self, player, day):
        """跨服务日刷新。缺陷：直接返回 False，既不刷新也不清累计。"""
        return False

    def scanned_count(self):
        return self.scanned
