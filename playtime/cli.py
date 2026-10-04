"""命令行入口：跑在线时长奖励样例。"""

import argparse

from .core import Rewards


def build_parser():
    parser = argparse.ArgumentParser(prog="playtime-reward", description="在线时长档位奖励")
    parser.add_argument("--sample", default="repeat", help="repeat / exact / dup / day / multi / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "repeat":
        book = Rewards([(1, 100)])
        book.tick("p", 1000, True)
        book.tick("p", 1000, True)
        print("played=%d" % book.played_ms("p"))
    elif args.sample == "exact":
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        print("claimable=%d" % len(book.claimable("p")))
    elif args.sample == "dup":
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        book.claim("p", 0)
        second = book.claim("p", 0)
        print("second=%s claimed=%d" % (str(second).lower(), len(book.claimed("p"))))
    elif args.sample == "day":
        book = Rewards([(1, 100)])
        book.tick("p", 60000, True)
        book.claim("p", 0)
        book.reset_day("p", 2)
        print("claimed=%d" % len(book.claimed("p")))
    elif args.sample == "multi":
        book = Rewards([(1, 100), (2, 200), (3, 300)])
        book.tick("p", 180000, True)
        print("claimable=%d" % len(book.claimable("p")))
    elif args.sample == "scan":
        book = Rewards([(1, 100)])
        for index in range(3000):
            book.tick("p-%d" % index, 60000, True)
        for _ in range(3000):
            book.claimable("p-0")
        print("scanned=%d" % book.scanned_count())
    else:
        raise SystemExit("需要 --sample repeat|exact|dup|day|multi|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
