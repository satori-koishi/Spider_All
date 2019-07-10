def calculation(expression):
    ChartDict = {'零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
                 '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
                 '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
                 '6': '6', '7': '7', '8': '8', '9': '9'}

    test = expression
    symbol = test[1]
    zz = ChartDict.keys()
    result = ''
    if symbol == '＋':
        symbol = '+'
    if symbol == '一':
        symbol = '-'

    number = ChartDict[test[0]]
    if test[2] in zz:
        number2 = ChartDict[test[2]]
    else:
        try:
            number2 = ChartDict[test[-1]]
        except:
            number2 = 1

    if symbol == 'x' or symbol == '乘' or symbol == 'X':
        result = int(number) * int(number2)

    elif symbol == '+' or symbol == '加':
        result = int(number) + int(number2)

    elif symbol == '-' or symbol == '减' or symbol == '－':
        result = int(number) - int(number2)

    elif symbol == '✲':
        result = int(number) * int(number2)

    elif symbol == '除':
        try:
            result = int(number) // int(number2)
        except:
            result = int(number) + int(number2)
    print(result)
    return result


calculation('3除零=')
