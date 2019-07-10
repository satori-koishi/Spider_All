# 验证码

import random
from PIL import Image, ImageFont, ImageDraw
import time

# 验证码文字

data1 = ['1', '2', '3', '4', '5', '6', '7', '8',
         '9', '0', '一', '二', '三', '四', '五', '六', '七', '八', '九', '零']
data2 = ['加', '减', '乘', '除', '+', '-', 'X', 'x', '乘,以', '除,以', '*', '加,上', '减,去']

dicnumber = {'1': 'heiti.ttf', '2': 'heiti.ttf', '3': 'heiti.ttf', '4': 'heiti.ttf', '5': 'heiti.ttf', '6': 'heiti.ttf',
             '7': 'heiti.ttf', '8': 'heiti.ttf', '=': 'songti.ttf', '✲': 'songti.ttf',
             '9': 'heiti.ttf', '0': 'heiti.ttf', '一': 'lishu.ttf', '二': 'lishu.ttf', '三': 'lishu.ttf', '四': 'lishu.ttf',
             '五': 'lishu.ttf', '六': 'lishu.ttf', '七': 'lishu.ttf',
             '八': 'lishu.ttf', '九': 'lishu.ttf', '零': 'lishu.ttf', '加': 'songti.ttf', '减': 'songti.ttf',
             '+': 'songti.ttf', '-': 'songti.ttf', 'X': 'songti.ttf', '乘': 'songti.ttf', '除': 'songti.ttf',
             '以': 'songti.ttf', '上': 'songti.ttf', '去': 'songti.ttf'}

charlist = ['heiti.ttf', 'songti.ttf', 'lishu.ttf']

for i in range(30000):
    datastr = []
    width = 90

    # 验证码高度

    height = 34

    mode = 'RGB'

    size = (width, height)

    color = "rgb(255,255,255)"

    img = Image.new(mode, size, color)  # 生成画布

    draw = ImageDraw.Draw(img)  # 创建画笔
    for x in range(4):

        if x == 1:
            datasuiji = random.randint(0, len(data2) - 1)
            data = data2[datasuiji]
            strlist = data.split(',')
            for s in strlist:
                datastr.append(s)
        elif x == 3:
            datastr.append('=')
        else:
            datasuiji = random.randint(0, len(data1) - 1)
            datastr.append(data1[datasuiji])
        i = 0
        if x == 3:
            for x in datastr[0:4]:
                print(random.choice(charlist))
                if x == '*':
                    datastr[1] = '✲'
                font = ImageFont.truetype(
                    font=random.choice(charlist), size=22)

                draw.text((10 + 20 * i + random.randint(0, 5), random.randint(-5, 5)), x, font=font,
                          fill=(random.randint(5, 250), random.randint(5, 250), random.randint(5, 250)))

                i += 1
    time.sleep(0.3)

    cc = ''.join(datastr[0:4]) + '_%s.jpg' % (int(time.time()))
    print(cc)
    # 1'E:\stable_2IGT\cnn_captcha\sample\new_train'
    img.save('E:/stable_2IGT/cnn_captcha/sample/new_train/%s' % cc, 'jpeg')
