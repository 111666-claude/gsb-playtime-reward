"""在线时长档位奖励：按真实时间累计在线时长、档位达标领取、跨服务日刷新。

口径见 README：同刻重复推进不重复累计、推进时间单调、达标用不小于、
领取幂等且有每日配额、跨服务日刷新、跨多档全部列出、可领档位指针推进。
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
            state = {"last": 0, "played": 0, "claimed": set(), "day": 1,
                     "claims": 0, "met": 0}
            self.players[player] = state
        return state

    def tick(self, player, now_ms, online):
        """推进在线时长：只计入与上次推进时刻之差，回退拒绝，离线不计。"""
        state = self._state(player)
        if now_ms < state["last"]:
            return False
        if online:
            state["played"] += now_ms - state["last"]
        state["last"] = now_ms
        return True

    def played_ms(self, player):
        """累计在线毫秒。"""
        return self._state(player)["played"]

    def _advance(self, state):
        """把达标指针推进到当前分钟数，只前进不重扫。"""
        minutes = state["played"] // MINUTE_MS
        met = state["met"]
        while met < len(self.tiers) and self.tiers[met][0] <= minutes:
            met += 1
        self.scanned += met - state["met"]
        state["met"] = met

    def claimable(self, player):
        """可领档位下标：已达标且未领取，按升序，一次跨多档全部列出。"""
        state = self._state(player)
        self._advance(state)
        return [index for index in range(state["met"])
                if index not in state["claimed"]]

    def claim(self, player, tier):
        """领取档位：同档同日只领一次，每日最多 max_claims 个。"""
        state = self._state(player)
        if tier < 0 or tier >= len(self.tiers):
            return False
        if tier in state["claimed"]:
            return False
        if state["claims"] >= self.max_claims:
            return False
        state["claimed"].add(tier)
        state["claims"] += 1
        return True

    def claimed(self, player):
        """已领档位。"""
        return sorted(self._state(player)["claimed"])

    def reset_day(self, player, day):
        """跨服务日刷新：只在新服务日生效一次，清零已领、计数与累计时长。"""
        state = self._state(player)
        if day <= state["day"]:
            return False
        state["day"] = day
        state["claimed"] = set()
        state["claims"] = 0
        state["played"] = 0
        state["last"] = 0
        state["met"] = 0
        return True

    def scanned_count(self):
        return self.scanned
