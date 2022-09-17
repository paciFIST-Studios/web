import random
import re


def parse_roll_request(request):
    # here, we use a try-except block, b/c it would be easy for the user to send us a bad request
    try:
        # https://stackoverflow.com/questions/12409894/fast-way-to-split-alpha-and-numeric-chars-in-a-python-string/12411196
        tokens =  re.findall(r"[^\W\d_]+|\d+|\+",  request)
        # print(f'tokens: {tokens}')
        _count = int(tokens[0])
        _size = int(tokens[2])
        _modifier = int(tokens[4]) if '+' in tokens else 0
        return dict(count=_count, size=_size, modifier=_modifier)
    except Exception as ex:
        # print(f'user exception: {ex}')
        # any malformed request will result in us returning the help message to the user
        return dict(help=True)


HELP_MESSAGE = 'Bad Request.  Try "XdY+Z", where X, Y, and Z are whole numbers greater than or equal to zero\n'


def roll_dice(data):
    if 'help' in data and data['help']:
        return HELP_MESSAGE

    if 'count' not in data:
        data['count'] = 1
    if 'size' not in data or data['size'] < 1:
        data['size'] = 6
    # if 'keen' not in data:
    #     data['keen'] = 0
    if 'modifier' not in data:
        data['modifier'] = 0

    roll = []
    total = data['modifier']
    random.seed()
    has_critical_fail = False
    has_critical_success = False
    for i in range(data['count']):
        roll.append(random.randint(1, data['size']))
        total += roll[i]
        if roll[i] == 1:
            has_critical_fail = True
        if roll[i] == data['size']:
            has_critical_success = True

    result = {
        'total': total
        , 'request': '{}d{}+{}'.format(data['count'], data['size'], data['modifier'])
        , 'rolls': roll
    }

    if data['count'] == 1:
        if has_critical_success:
            result['critical_success'] = True
        elif has_critical_fail:
            result['critical_failure'] = True

    return result
