import re
import logging
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG)

NICK_RGX = '[\d\w!@#]+'

testcase = \
    '''
                               jellytot121 -- guv    chill
                                               |`------|-----------.
                                       souless |     andastra .-- wren
                    .-----------------------|--|-------|----|-|---|----.
                    |.--------------------- thleen ----|---.| |   |    |
                    ||                      .-|--|-----|-- teg! --|-- locust
                    ||                      | |  |     |   ||||   |   |
                    ||         .------------|-|--|-----|---'|||   |   |
    mirrorshades --.||         |            | |  |     |   .'|`---|---|-----.
                   ||| starz --|-- synder --|-|--|-- lillith |  basshead    |
      webkitten --.|||  |      |    .-------|-'  |   |       |  |           |
                  ||||.-'   goddess |  the_brain |   |.---- phlik -- nykwil |
      mosquito --.|||||          |  |        |   |   ||      | |            |
                 |||||| lipflaps |  |        `-- mph!@@ -----|-|---- lee777 |
    LdyMuriel --.||||||.-'       |  |        .---'|   |      | daze         |
                ||||||||         |  | .------|----|---|------'              |
      Kalika -- IceHeart --------|--|-|------|----|-- virago ---- chexbitz  |
                |||||||`-.     UncleRed      |    |    |   |          |     |
      Serenla --'|||||| Erato  | |  | |      | .--'  mre   ewheat   vioiet  |
                 |||||`-.      | |  | `------|-|--.                         |
      Berdiene --'|||| flutterbi | serendipity |  |                         |
                  |||`-----------|-------------|--|------- satsuki ---------'
           Pyra --'|`-- FillerBunny -----------'  kilgore ---'|  |
            |      |                                |         |  roach
        Roamer    McGrady                          spinningmind
    '''


def get_nick(sc, i, j):
    start, end = j, j
    while sc[i][start] != ' ':
        start -= 1
    start += 1
    while sc[i][end] != ' ':
        end += 1
    logging.debug(f'Returning nick from get_nick: {start},{end} -- {sc[i][start:end]}')
    return sc[i][start:end]

def follow(sc, i, j, d):
    cur = sc[i][j]
    logging.debug(f'In follow {d}: {i},{j}')
    if d == 'left':
        if cur in {'-', '|'}:
            return follow(sc, i, j - 1, 'left')
        elif cur in {'.'}:
            return follow(sc, i + 1, j, 'down')
        elif cur in {"'", '`'}:
            return follow(sc, i, j, 'up')
        elif cur == ' ':
            logging.debug(f'Found nick left at {i},{j}: {sc[i][:j]}')
            return re.findall(f'{NICK_RGX}$', sc[i][:j]).pop()
        else:
            raise ValueError(f'The fuck is wrong with this map: {cur} at {i},{j}')
    elif d == 'right':
        if cur in {'-', '|'}:
            return follow(sc, i, j + 1, 'right')
        elif cur in {'.'}:
            return follow(sc, i + 1, j, 'down')
        elif cur in {"'", '`'}:
            return follow(sc, i, j, 'up')
        elif cur == ' ':
            logging.debug(f'Found nick right at {i},{j}: "{sc[i][j + 1:]}"')
            return re.findall(f'^{NICK_RGX}', sc[i][j + 1:]).pop()
        else:
            raise ValueError(f'The fuck is wrong with this map: {cur} at {i},{j}')
    elif d == 'up':
        if cur in {'|', "'", '`'}:
            return follow(sc, i - 1, j, 'up')
        elif cur in {'.'}:
            if sc[i][j - 1] in {'-', '`'}:
                j = j - 1
                d = 'left'
            elif sc[i][j + 1] in {'-', "'"}:
                j = j + 1
                d = 'right'
            else:
                raise ValueError(f'The fuck is wrong with this map: {cur} at {i},{j}')
            return follow(sc, i, j, d)
        elif re.match(NICK_RGX, cur):
            logging.debug(f'Found nick up at {i}, {j}: {sc[i][j]}')
            return get_nick(sc, i, j)
        else:
            return None
    elif d == 'down':
        if cur in {'|'}:
            return follow(sc, i + 1, j, 'down')
        elif cur in {'`', "'"}:
            if sc[i][j - 1] in {'-', '.'}:
                j = j - 1
                d = 'left'
            elif sc[i][j + 1] in {'-', '.'}:
                j = j + 1
                d = 'right'
            else:
                raise ValueError(f'The fuck is wrong with this map: {cur} at {i},{j}')
            return follow(sc, i, j, d)
        elif re.match(NICK_RGX, cur):
            logging.debug(f'Found nick up at {i}, {j}: {sc[i][j]}')
            return get_nick(sc, i, j)
        else:
            return None
    else:
        raise ValueError('The fuck you talking about direction {d}')

def find_leftright(sc, nick, i, j):
    '''Check left lover for nick starting at i,j'''
    # check left
    ret = list()
    if re.search(f'- {nick}', sc[i]):
        start = j - 2
        d = 'left'
        lover = follow(sc, i, start, d)
        if lover:
            ret.append(lover)
    if re.search(f'{nick} -', sc[i]):
        start = j + len(nick) + 2
        d = 'right'
        lover = follow(sc, i, start, d)
        if lover:
            ret.append(lover)
    return ret

def find_ups(sc, nick, i, j):
    '''Check all lovers up from nick at i,j'''
    if i == 0:
        return []
    ret = list()
    for k in range(j, j + len(nick)):
        logging.debug(f'Searching up for {nick}: {i},{k}')
        lover = follow(sc, i - 1, k, 'up')
        logging.debug(f'lover in up: {lover}')
        if lover:
            ret.append(lover)
    return ret

def find_downs(sc, nick, i, j):
    '''Check all lovers down from nick at i,j'''
    if i == len(sc) - 1:
        return []
    ret = list()
    for k in range(j, j + len(nick)):
        logging.debug(f'Searching down for {nick}: {i + 1},{k}')
        lover = follow(sc, i + 1, k, 'down')
        logging.debug(f'lover in down for {nick}: {lover}')
        if lover:
            ret.append(lover)
    return ret

def parse_sexchart(sc):
    '''Takes a sexcharge in ascii form as an array of strings'''
    directions = [find_leftright, find_ups, find_downs]
    ret = defaultdict(list)
    for i in range(len(sc)):
        nicks = re.findall('[\d\w!@#]+', sc[i])
        for nick in nicks:
            j = sc[i].find(nick)
            for direction in directions:
                lovers = direction(sc, nick, i, j)
                if lovers:
                    logging.debug(f'Extending {nick}\'s lovers by {lovers} with direction {direction}')
                    ret[nick].extend(lovers)
    return ret

def clean_sexchart(sc):
    sc = sc.strip('\n').split('\n')
    m = max(map(len, sc))
    return [format(s, f'<{m}') for s in sc]


if __name__ == '__main__':
    sc = testcase
    sc = clean_sexchart(sc)
    ps = parse_sexchart(sc)
    print(ps)
    for key in ps:
        print(key, ps[key])
    print(len(ps))
