import datetime
import os
import notify
import json
import logging
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import sys


DKYC = ''
DKTIME = ''


class report:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.__client = webdriver.Chrome(service=Service(
            '/usr/bin/chromedriver'), options=chrome_options)
        self.__wait = WebDriverWait(self.__client, 10, 0.5)

    def __get_element_by_xpath(self, xpath: str):
        return self.__wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def login(self, username: str, password: str) -> bool:
        self.__username = username
        self.__flag = False
        try:
            self.__client.get(
                "https://yqfk.zcmu.edu.cn:6006/iForm/2714073AABBBDF56AF8E54")
            ids_button = self.__get_element_by_xpath(
                '/html/body/frame-options/div/div/div[2]/div/div/div[3]/ul/li[3]/a')
            ids_button.click()
            uername_input = self.__get_element_by_xpath(
                '/html/body/div[1]/div[4]/div/form/table/tbody/tr[1]/td/input[1]')
            psw_input = self.__get_element_by_xpath(
                '/html/body/div[1]/div[4]/div/form/table/tbody/tr[2]/td/input[1]')
            login_button = self.__get_element_by_xpath(
                '/html/body/div[1]/div[4]/div/form/table/tbody/tr[4]/td/input')
            uername_input.send_keys(username)
            psw_input.send_keys(password)
            login_button.click()
            time.sleep(1)
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def do(self) -> bool:
        try:
            js = ''' iduo.http.parseDataSource("SELECT_XSJKDK$" + iduo.user.Sys_UserId).then(data => {
        if (data.length > 0) {
        iduo.data.setUIValue('PHONE', data[0].PHONE);
        iduo.data.setUIValue('JTZZ', data[0].JTZZ);
        iduo.data.setUIValue('XXDZ', data[0].XXDZ);
        iduo.data.setUIValue('MQJZDZ', data[0].MQJZDZ);
        iduo.data.setUIValue('MQJZDZGD', data[0].MQJZDZGD);
        iduo.data.setUIValue('SFLX', data[0].SFLX);
        iduo.data.setUIValue('JJLXRXM', data[0].JJLXRXM);
        iduo.data.setUIValue('JJLXRSJHM', data[0].JJLXRSJHM);
        //iduo.data.setUIValue('BRSTSFYBS', data[0].BRSTSFYBS);
        //iduo.data.setUIValue('BRHGTSHDJSSSRNSFQGYXDD', data[0].BRHGTSHDJSSSRNSFQGYXDD);
        iduo.data.setUIValue('MQBRDSJZT', data[0].MQBRDSJZT);
        iduo.data.setUIValue('MQBRGLZT', data[0].MQBRGLZT);
        iduo.data.setUIValue('MQJRDSJZT', data[0].MQJRDSJZT);
        iduo.data.setUIValue('JRSFZXHLX', data[0].JRSFZXHLX);
        iduo.data.setUIValue('NSQDJKMYSSSM', data[0].NSQDJKMYSSSM);
        iduo.data.setUIValue('KXHZSD', data[0].KXHZSD);
        iduo.data.setUIValue('DTDXQK', data[0].DTDXQK);
        iduo.data.setUIValue('BRTWZK', data[0].BRTWZK);
        iduo.data.setUIValue('XXDZ', data[0].XXDZ);
        iduo.data.setUIValue('SFHSJC', data[0].SFHSJC);}})'''
            Q7 = self.__get_element_by_xpath(
                '//*[@id="iform"]/div[1]/div[3]/form/div[14]/div/div/div[2]/div/div/div/div[1]/div/div[6]/div/i')  # 本人身体是否有不适
            Q7.click()
            Q8 = self.__get_element_by_xpath(
                '//*[@id="iform"]/div[1]/div[3]/form/div[16]/div/div/div[2]/div/div/div/div[1]/div/div[3]/div')  # 本人7日内是否去过以下地点
            Q8.click()
            time.sleep(1)
            self.__client.execute_script(js)
            time.sleep(5)
            stateMent = self.__get_element_by_xpath(
                '/html/body/div[1]/div[2]/div[1]/div[3]/form/div[39]/div/div/div[2]/div/div/div/div[1]/div/div/div')
            stateMent.click()
            submit_button = self.__get_element_by_xpath(
                '/html/body/div[1]/div[2]/div[1]/div[4]/div/button[1]')
            submit_button.click()
            time.sleep(2)
            confirm_button = self.__get_element_by_xpath(
                '/html/body/div[3]/div[3]/button[2]')
            confirm_button.click()
        except Exception as e:
            logging(e)
            return False
        else:
            self.__flag = True
            return True

    def check(self) -> bool:
        url = 'https://yqfk.zcmu.edu.cn:5010/Noauth/api/form/api/DataSource/GetDataSourceByNo?sqlNo=SELECT_XSJKDK${}'
        res = json.loads(requests.get(url.format(self.__username)).text)
        global DKYC
        DKYC = res['data'][0]['DKYC']
        # print(res)
        logging.info('Checking data:{}'.format(res))
        if len(res['data']) == 0:
            return False
        unix_dtime = int(time.mktime(datetime.date.today().timetuple()))
        unix_ctime = int(time.mktime(time.strptime(
            res['data'][0]['CURRENTTIME'], '%Y-%m-%d %H:%M:%S')))
        global DKTIME
        DKTIME = res['data'][0]['CURRENTTIME']
        logging.info('unix_dtime: {}, unix_ctime:{}'.format(
            unix_dtime, unix_ctime))
        return True if unix_dtime <= unix_ctime else False

    def pushplus_bot(self, title: str, content: str, token: str, topic: str) -> None:
        # """
        # 通过 push+ 推送消息。
        # """

        print("PUSHPLUS 服务启动")

        url = "http://www.pushplus.plus/send"
        data = {
            "token": token,
            "title": title,
            "content": content,
            "topic": topic,
        }
        body = json.dumps(data).encode(encoding="utf-8")
        headers = {"Content-Type": "application/json"}
        response = requests.post(url=url, data=body, headers=headers).json()

        if response["code"] == 200:
            print("PUSHPLUS 推送成功！")

        else:

            url_old = "http://pushplus.hxtrip.com/send"
            headers["Accept"] = "application/json"
            response = requests.post(
                url=url_old, data=body, headers=headers).json()

            if response["code"] == 200:
                print("PUSHPLUS(hxtrip) 推送成功！")

            else:
                print("PUSHPLUS 推送失败！")

    def reload(self):
        self.__client.get(
            'https://yqfk.zcmu.edu.cn:6006/iForm/2714073AABBBDF56AF8E54')

    def destruct(self):
        self.__client.quit()

    def status(self) -> bool:
        return self.__flag


def main(dev: bool = False):
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    DD_BOT_TOKEN = os.environ["DD_BOT_TOKEN"]
    DD_BOT_SECRET = os.environ["DD_BOT_SECRET"]
    TOKEN = os.environ["TOKEN"]

    user_list = username.split(',')
    passwd_list = password.split(',')

    for i in range(len(user_list)):
        re = report()
        if i != 0:
            PUSH_PLUS_TOKEN_list = TOKEN.split(',')
            token = PUSH_PLUS_TOKEN_list[i]
        if re.login(user_list[i], passwd_list[i]):
            if re.check():
                # if dev:
                #     return '已经打过卡了！'
                if DD_BOT_TOKEN:
                    notify.title = 'Already'
                    notify.content = '用户:%s\n已经打过卡了！\n打卡状态:%s\n打卡时间:%s' % (
                        user_list[i], DKYC, DKTIME)
                    notify.main()

                    if i != 0:
                        if token:
                            re.pushplus_bot('Already', '用户:%s\n已经打过卡了！\n打卡状态:%s\n打卡时间:%s' % (
                                user_list[i], DKYC, DKTIME), token, '')
            else:
                # if dev:
                #     return '打卡成功！'
                while re.check() != True:
                    if re.do():
                        re.check()
                        if DKYC == '正常':
                            if DD_BOT_TOKEN:
                                notify.title = 'Succeeded'
                                notify.content = '用户:%s\n打卡成功！\n打卡状态:%s\n打卡时间:%s' % (
                                    user_list[i], DKYC, DKTIME)
                                notify.main()

                                if i != 0:
                                    if token:
                                        re.pushplus_bot('Succeeded', '用户:%s\n打卡成功！\n打卡状态:%s\n打卡时间:%s' % (
                                            user_list[i], DKYC, DKTIME), token, '')
                            break
                        else:
                            if DD_BOT_TOKEN:
                                notify.title = 'Abormal'
                                notify.content = '用户:%s,打卡异常，请检查！'
                                notify.main()

                                if i != 0:
                                    if token:
                                        re.pushplus_bot(
                                            'Abormal', '用户:%s,打卡异常，请检查！', token, '')
                            break

                    retries -= 1
                    re.reload()
                else:
                    # if dev:
                    #     return '打卡失败！'
                    logging.info('error: {}'.format(username))
                    if DD_BOT_TOKEN:
                        notify.title = 'ERROR'
                        notify.content = '用户:%s\n打卡失败！' % (user_list[i])
                        notify.main()

                        if i != 0:
                            if token:
                                re.pushplus_bot('ERROR', '用户:%s\n打卡失败！' % (
                                    user_list[i]), token, '')
    re.destruct()


if __name__ == "__main__":
    main()
