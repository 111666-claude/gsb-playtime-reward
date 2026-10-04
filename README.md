# playtime-reward

在线时长档位奖励：按真实时间累计在线时长、档位达标领取、跨服务日刷新，只用 Python 标准库。

```
python3 -m playtime.cli --sample repeat
python3 -m playtime.cli --sample ooo
python3 -m playtime.cli --sample quota
python3 -m playtime.cli --sample day
python3 -m playtime.cli --sample dup
python3 -m playtime.cli --sample multi
python3 -m playtime.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **累计与达标**：`tick` 只把 `now_ms` 与上一次推进时刻之差计入在线时长，同一时刻重复推进不重复累计，
  离线区间不计；累计在线分钟数不小于档位分钟数即可领取，正好等于档位分钟数算达标。
- **推进单调**：推进到比当前更早的时刻一律拒绝并返回 False，累计时长不变。
- **领取与配额**：同一服务日内同一档位只能领一次，重复领取返回 False；同一服务日最多领 `max_claims`
  个档位，超出返回 False。
- **跨服务日**：`reset_day` 只在新服务日生效一次，已领档位、当日领取计数与累计时长一起清零，
  返回这次调用是否真的刷新了。
- **可领列表**：列出所有已达标且未领取的档位下标，按档位升序；一次跨过多个档位时全部列出。
- **代价**：可领档位用指针推进，不重扫整张档位表，`scanned_count()` 不随档位数乘查询次数增长。
- **不变量**：同一服务日内同一档位不会领第二次，当日领取数不超过 `max_claims`，同一串序列重复执行结果相同。
- **规模**：10 万玩家、每秒 10 万次查询，单次摊还 O(1)。

## 输出契约（不改格式）

```
played=..
second=.. played=..
third=.. claimed=..
second=.. claimed=..
claimable=..
scanned=..
```

## 目录

```
playtime/core.py   时长累计、推进时间线、领取配额与跨日刷新
playtime/cli.py    命令行入口
tests/             unittest 用例
```
