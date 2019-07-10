import random
import time, re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import requests
from io import BytesIO
import base64


class Vincent(object):
    def __init__(self):
        chrome_option = webdriver.ChromeOptions()
        # chrome_option = webdriver.PhantomJS()
        # chrome_option.set_headless()

        self.driver = webdriver.Chrome(chrome_options=chrome_option)
        # self.driver = webdriver.PhantomJS()
        # self.driver =webdriver.Chrome("D:\Google\Chrome\Application\chromedriver.exe")
        # self.driver.set_window_size(500, 500)

    def visit_index(self):
        # self.driver.get("https://www.Vincent.com/")
        self.driver.get("http://zj.gsxt.gov.cn/index.html")
        time.sleep(4)
        self.driver.find_element_by_id('keyword').send_keys('浙江大成工程项目管理有限公司')
        WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable((By.ID, 'btn_query')))
        reg_element = self.driver.find_element_by_id("btn_query")
        reg_element.click()
        try:
            WebDriverWait(self.driver, 10, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="geetest_panel_next"]')))
        except TimeoutException as e:
            print('点击超时正在处理', e)
            self.driver.close()
            repaly_spider_time = random.randint(2, 5)
            time.sleep(repaly_spider_time)
            h = Vincent()
            h.visit_index()

        # 进入模拟拖动流程
        self.analog_drag()

    def analog_drag(self):
        # 鼠标移动到拖动按钮，显示出拖动图片
        # element = self.driver.find_element_by_xpath('//div[@class="geetest_slider_button"]')
        # ActionChains(self.driver).move_to_element(element).perform()
        # time.sleep(1)
        # # # 刷新一下极验图片
        # element = self.driver.find_element_by_xpath('//a[@class="geetest_refresh_1"]')
        # element.click()
        time.sleep(1.5)

        # 获取图片地址和位置坐标列表
        JS = 'return document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL("image/png");'
        im_info = self.driver.execute_script(JS)
        im_base64 = im_info.split(',')[1]  # 拿到base64编码的图片信息
        im_bytes = base64.b64decode(im_base64)  # 转为bytes类型
        with open('cut.png', 'wb') as f:  # 保存图片到本地
            f.write(im_bytes)
        JS = 'return document.getElementsByClassName("geetest_canvas_fullbg geetest_fade geetest_absolute")[' \
             '0].toDataURL("image/png"); '
        im_info = self.driver.execute_script(JS)
        im_base64 = im_info.split(',')[1]  # 拿到base64编码的图片信息
        im_bytes = base64.b64decode(im_base64)  # 转为bytes类型
        with open('full.png', 'wb') as f:  # 保存图片到本地
            f.write(im_bytes)
        cut = Image.open('cut.png')
        full = Image.open('full.png')
        x = self.get_offset_distance(cut, full)
        self.start_move(x)
        # try:
        #     WebDriverWait(self.driver, 5, 0.5).until(
        #         EC.element_to_be_clickable((By.XPATH, '//div[@class="geetest_result_title"]')))
        #
        #     print("验证失败")
        #     return
        # except TimeoutException as e:
        #     pass
        time.sleep(2)
        all_company_url = self.driver.find_elements_by_xpath('//div[@class="ads-sci-line"]')
        # print(s)
        self.set_url = set()
        if len(all_company_url) == 0:
            print("滑动解锁失败,继续尝试")
            self.analog_drag()
        else:
            print("滑动解锁成功")
            time.sleep(1)
            # 点击提示
            self.all_company_url()
            print(self.my_u_set)

    def all_company_url(self):
        all_company_url = self.driver.find_elements_by_xpath('//a[@class="search_list_item db"]')
        self.my_u_set = set()
        for a in all_company_url:
            self.my_u_set.add(a.get_attribute('href'))
        more_company_information = self.driver.find_elements_by_xpath('//div[@class="pagination"]/form/a')

        if not len(more_company_information) == 0:
            myset = set()
            for m in more_company_information:
                print(len(m.text), m.text)
                try:
                    n = int(m.text)
                    if not n in myset:
                        time.sleep(5)
                        m.click()
                        myset.add(n)
                        self.all_company_url()
                    continue
                except ValueError as e:
                    pass

    # 判断颜色是否相近
    def is_similar_color(self, x_pixel, y_pixel):
        for i, pixel in enumerate(x_pixel):
            if abs(y_pixel[i] - pixel) > 50:
                return False
        return True

    # 计算距离
    def get_offset_distance(self, cut_image, full_image):
        for x in range(cut_image.width):
            for y in range(cut_image.height):
                cpx = cut_image.getpixel((x, y))
                fpx = full_image.getpixel((x, y))
                if not self.is_similar_color(cpx, fpx):
                    img = cut_image.crop((x, y, x + 50, y + 40))
                    # 保存一下计算出来位置图片，看看是不是缺口部分
                    img.save("1.png")
                    return x
        # cut_image_url, cut_location = self.get_image_url('//div[@class="gt_cut_bg_slice"]')
        # full_image_url, full_location = self.get_image_url('//div[@class="gt_cut_fullbg_slice"]')

        # 根据坐标拼接图片
        # cut_image = self.mosaic_image(cut_image_url, cut_location)
        # full_image = self.mosaic_image(full_image_url, full_location)

        # 保存图片方便查看
        # cut_image.save("cut.jpg")
        # full_image.save("full.jpg")

        # 根据两个图片计算距离
        # distance = self.get_offset_distance(cut_image, full_image)
        #
        # # 开始移动
        # self.start_move(distance)
        #
        # # 如果出现error
        # try:
        #     WebDriverWait(self.driver, 5, 0.5).until(
        #         EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_ajax_tip gt_error"]')))
        #
        #     print("验证失败")
        #     return
        # except TimeoutException as e:
        #     pass
        #
        # # 判断是否验证成功
        # s = self.driver.find_elements_by_xpath('//*[@id="wrap1"]/div[3]/div/div/p')
        # self.set_url = set()
        # if len(s) == 0:
        #     print("滑动解锁失败,继续尝试")
        #     self.analog_drag()
        # else:
        #     print("滑动解锁成功")
        #     time.sleep(1)
        #     # 点击提示
        #     self.driver.find_element_by_xpath('//button/span').click()
        #     time.sleep(3)
        # ss=self.driver.find_element_by_xpath('//div[@class="tableContent page-item"]')
        # print(ss)
        # for s in ss:
        #     print(s.get_attribute("onclick"))
        # zz=self.driver.find_element_by_xpath('//*[@id="wrap1"]/div[3]/div/div')
        # print(zz)
        # time.sleep(3)
        # corporate_url = self.driver.find_element_by_xpath('//div[@class="tableContent page-item"]').get_attribute("onclick")
        # corporate_url = self.driver.find_element_by_xpath('//div[@class="tableContent"]')
        # print(corporate_url)

    # 开始移动
    def start_move(self, distance):
        time.sleep(1)
        element = self.driver.find_element_by_xpath('//div[@class="geetest_slider_button"]')

        # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
        # distance -= element.size.get('width') / 2
        distance -= 4.5
        # print('设置之后的位置', distance)

        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(element).perform()
        time.sleep(0.5)
        while distance > 0:
            if distance > 10:
                # 如果距离大于10，就让他移动快一点
                span = random.randint(5, 8)
            else:
                # 快到缺口了，就移动慢一点
                span = random.randint(2, 3)
            ActionChains(self.driver).move_by_offset(span, 0).perform()
            distance -= span
            time.sleep(random.randint(10, 50) / 100)

        # ActionChains(self.driver).move_by_offset(distance, 1).perform()
        ActionChains(self.driver).release(on_element=element).perform()

    # # 获取图片和位置列表
    # def get_image_url(self, xpath):
    #     link = re.compile('background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;')
    #     # print(link)
    #     elements = self.driver.find_elements_by_xpath(xpath)
    #     print(elements,'图片url')
    #     image_url = None
    #     location = list()
    #     for element in elements:
    #         style = element.get_attribute("style")
    #         groups = link.search(style)
    #         url = groups[1]
    #         x_pos = groups[2]
    #         y_pos = groups[3]
    #         location.append((int(x_pos), int(y_pos)))
    #         image_url = url
    #     return image_url, location
    #
    # # 拼接图片
    # def mosaic_image(self, image_url, location):
    #     resq = requests.get(image_url)
    #     file = BytesIO(resq.content)
    #     img = Image.open(file)
    #     image_upper_lst = []
    #     image_down_lst = []
    #     # print(location)
    #     for pos in location:
    #         # print(pos)
    #         if pos[1] == 0:
    #             # y值==0的图片属于上半部分，高度58
    #             image_upper_lst.append(img.crop((abs(pos[0]), 0, abs(pos[0]) + 10, 58)))
    #         #   [157,0,167,58]
    #         else:
    #             # y值==58的图片属于下半部分
    #             image_down_lst.append(img.crop((abs(pos[0]), 58, abs(pos[0]) + 10, img.height)))
    #
    #     x_offset = 0
    #     # 创建一张画布，x_offset主要为新画布使用
    #     new_img = Image.new("RGB", (260, img.height))
    #     for img in image_upper_lst:
    #         new_img.paste(img, (x_offset, 58))
    #         x_offset += img.width
    #
    #     x_offset = 0
    #     for img in image_down_lst:
    #         new_img.paste(img, (x_offset, 0))
    #         x_offset += img.width
    #     return new_img

    # 判断颜色是否相近
    # def is_similar_color(self, x_pixel, y_pixel):
    #     for i, pixel in enumerate(x_pixel):
    #         if abs(y_pixel[i] - pixel) > 50:
    #             return False
    #     return True
    #
    # # 计算距离
    # def get_offset_distance(self, cut_image, full_image):
    #     for x in range(cut_image.width):
    #         for y in range(cut_image.height):
    #             cpx = cut_image.getpixel((x, y))
    #             fpx = full_image.getpixel((x, y))
    #             if not self.is_similar_color(cpx, fpx):
    #                 img = cut_image.crop((x, y, x + 50, y + 40))
    #                 # 保存一下计算出来位置图片，看看是不是缺口部分
    #                 img.save("1.jpg")
    #                 return x

    # 开始移动
    # def start_move(self, distance):
    #     element = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
    #
    #     # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
    #     distance -= element.size.get('width') / 2
    #     distance += 15
    #
    #     # 按下鼠标左键
    #     ActionChains(self.driver).click_and_hold(element).perform()
    #     time.sleep(0.5)
    #     while distance > 0:
    #         if distance > 10:
    #             # 如果距离大于10，就让他移动快一点
    #             span = random.randint(5, 8)
    #         else:
    #             # 快到缺口了，就移动慢一点
    #             span = random.randint(2, 3)
    #         ActionChains(self.driver).move_by_offset(span, 0).perform()
    #         distance -= span
    #         time.sleep(random.randint(10, 50) / 100)
    #
    #     # ActionChains(self.driver).move_by_offset(distance, 1).perform()
    #     ActionChains(self.driver).release(on_element=element).perform()


if __name__ == "__main__":
    h = Vincent()
    h.visit_index()

# http://static.geetest.com/pictures/gt/c4ca4238a/c4ca4238a.webp
# http://static.geetest.com/pictures/gt/c4ca4238a/bg/03eb9ded9.webp
