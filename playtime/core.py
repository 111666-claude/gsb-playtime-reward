"""在线时长档位奖励：按真实时间累计在线时长、档位达标领取、跨服务日刷新。"""

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
            state = {
                "last": 0,
                "played": 0,
                "claimed": set(),
                "claims": 0,
                "day": 1,
                "next": 0,
                "avail": [],
            }
            self.players[player] = state
        return state

    def tick(self, player, now_ms, online):
        """推进在线时长：只累计与上次推进时刻之差，回退拒绝，离线不计。"""
        state = self._state(player)
        if now_ms < state["last"]:
            return False
        if online:
            state["played"] += now_ms - state["last"]
        state["last"] = now_ms
        return True

    def _refresh(self, state):
        """指针推进已达标档位，每个档位全程只扫一次。"""
        minutes = state["played"] // MINUTE_MS
        tiers = self.tiers
        index = state["next"]
        while index < len(tiers) and minutes >= tiers[index][0]:
            if index not in state["claimed"]:
                state["avail"].append(index)
            index += 1
            self.scanned += 1
        state["next"] = index

    def played_ms(self, player):
        """累计在线毫秒。"""
        return self._state(player)["played"]

    def claimable(self, player):
        """可领档位下标：已达标且未领取，按档位升序。"""
        state = self._state(player)
        self._refresh(state)
        return list(state["avail"])

    def claim(self, player, tier):
        """领取档位：同档每日只领一次，当日最多 max_claims 个。"""
        state = self._state(player)
        if tier in state["claimed"]:
            return False
        if state["claims"] >= self.max_claims:
            return False
        state["claimed"].add(tier)
        state["claims"] += 1
        if tier in state["avail"]:
            state["avail"].remove(tier)
        return True

    def claimed(self, player):
        """已领档位，按档位升序。"""
        return sorted(self._state(player)["claimed"])

    def reset_day(self, player, day):
        """跨服务日刷新：只在新服务日生效一次，清零已领、计数与累计时长。"""
        state = self._state(player)
        if day <= state["day"]:
            return False
        state["day"] = day
        state["played"] = 0
        state["claimed"] = set()
        state["claims"] = 0
        state["next"] = 0
        state["avail"] = []
        return True

    def scanned_count(self):
        return self.scanned
