"""Operations with stats file"""
import json
import operator


def load_stats():
    """Get users stats from file"""
    res = []
    try:
        with open('userstats.data', 'r') as f:
            res = json.load(f)
    except Exception:
        pass

    return res


def save_stats(username, points):
    """Save user stats"""
    stats = dict(load_stats())
    stats[username] = points if points > stats.get(username, 0) else stats[username]
    stats = sorted(stats.iteritems(), key=operator.itemgetter(1), reverse=True)

    try:
        with open('userstats.data', 'w') as f:
            json.dump(stats[:5], f)
    except Exception:
        pass
