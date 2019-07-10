import requests

# print(zz.text)
import json
import re
from requests.cookies import RequestsCookieJar

cookie_jar = RequestsCookieJar()
url_zz = 'http://jgpt.lnzb.cn/EpointWebBuilder_ln/getZtxxInfoAction.action?cmd=getZtxxInfo'
token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'


def start():
    post_data = {'type': '13', 'pageindex': '0', 'pagesize': '12'}
    zz = requests.post(url=url_zz, data=post_data)
    keep(zz)


def keep(zz):
    Ln_json_data = json.loads(zz.text)
    Ln_json_data = dict(Ln_json_data)
    data = json.loads(Ln_json_data['custom'])
    all_data = data['EpointDataBody']['COUNT']
    # print(all_data)
    page = all_data // 12 + 1
    print(page)
    while True:
        page -= 1
        if page != -1:
            post_data = {'type': '13', 'pageindex': str(page), 'pagesize': '12'}
            cc = requests.post(url=url_zz, data=post_data)
            company_info(cc)


def company_info(cc):
    ln_json_data = json.loads(cc.text)
    ln_json_data = dict(ln_json_data)
    data = json.loads(ln_json_data['custom'])
    company = data['EpointDataBody']['DATA']['UserArea']
    company_data = json.loads(company)
    for c_url in company_data:
        danweiguid = c_url['danweiguid']
        url = c_url['url']
        vv = requests.get(url=url)
        uu = 'http://218.60.149.226/PSPFrame/huiyuaninfomis2/backend/shigonginfo/shiGongInfoDetailRead_LnAction' \
             '.action?cmd=page_Load&ViewType=2&DanWeiType=13&DanWeiGuid=%s&CurrentDanWeiGuid=%s&isCommondto=true' % (
                 danweiguid, danweiguid)
        data = {
            'commonDto': '[{"id":"danweiname","bind":"hyUnitComInfo.danweiname","type":"outputtext"},{"id":"isyl",'
                         '"bind":"dataBean.isyl","type":"outputtext","code":"是否","dataOptions":"{'
                         'code:_EpSingleQuotes_是否_EpSingleQuotes_}"},{"id":"englishname",'
                         '"bind":"hyUnitComInfo.englishname","type":"outputtext"},{"id":"duns",'
                         '"bind":"dataBean.duns","type":"outputtext"},{"id":"unitorgnum",'
                         '"bind":"hyUnitComInfo.unitorgnum","type":"outputtext"},{"id":"mini-8","bind":"btnA004",'
                         '"type":"output"},{"id":"faren","bind":"hyUnitComInfo.faren","type":"outputtext"},'
                         '{"id":"danweitype","bind":"dataBean.danweitype","type":"outputtext","code":"单位类别",'
                         '"dataOptions":"{code:_EpSingleQuotes_单位类别_EpSingleQuotes_}"},{"id":"dwattribute",'
                         '"bind":"dataBean.dwattribute","type":"outputtext","code":"单位属性","dataOptions":"{'
                         'code:_EpSingleQuotes_单位属性_EpSingleQuotes_}"},{"id":"webaddress",'
                         '"bind":"hyUnitComInfo.webaddress","type":"outputtext"},{"id":"industryname",'
                         '"bind":"dataBean.industryname","type":"outputtext"},{"id":"country",'
                         '"bind":"hyUnitComInfo.country","type":"outputtext","code":"国别/地区","dataOptions":"{'
                         'code:_EpSingleQuotes_国别/地区_EpSingleQuotes_}"},{"id":"areaname",'
                         '"bind":"hyUnitComInfo.areaname","type":"outputtext"},{"id":"baozhengjinbank",'
                         '"bind":"hyUnitComInfo.baozhengjinbank","type":"outputtext"},{"id":"baozhengjinaccount",'
                         '"bind":"hyUnitComInfo.baozhengjinaccount","type":"outputtext"},{"id":"localemail",'
                         '"bind":"dataBean.localemail","type":"outputtext"},{"id":"localmobile",'
                         '"bind":"dataBean.localmobile","type":"outputtext"},{"id":"supplyarea",'
                         '"bind":"dataBean.supplyarea","type":"outputtext"},{"id":"zipcode",'
                         '"bind":"dataBean.zipcode","type":"outputtext"},{"id":"waibuyewuyxq",'
                         '"bind":"dataBean.waibuyexuyxq","type":"outputtext","format":"yyyy-MM-dd","dataOptions":"{'
                         'format:_EpSingleQuotes_yyyy-MM-dd_EpSingleQuotes_}"},{"id":"address",'
                         '"bind":"dataBean.address","type":"outputtext"},{"id":"statuscode",'
                         '"bind":"dataBean.statuscode","type":"outputtext","code":"帐号状态","dataOptions":"{'
                         'code:_EpSingleQuotes_帐号状态_EpSingleQuotes_}"},{"id":"mini-25","bind":"dataBean.auditstatus",'
                         '"type":"outputtext","code":"验证状态","dataOptions":"{'
                         'code:_EpSingleQuotes_验证状态_EpSingleQuotes_}"},{"id":"auditstatus",'
                         '"bind":"dataBean.auditstatus","type":"outputtext"},{"id":"backreason",'
                         '"bind":"dataBean.backreason","type":"outputtext"},{"id":"licencenum",'
                         '"bind":"hyUnitComInfo.licencenum","type":"outputtext"},{"id":"mini-29","bind":"btnA001",'
                         '"type":"output"},{"id":"companytype","bind":"hyUnitComInfo.companytypename",'
                         '"type":"outputtext"},{"id":"zhuceziben","bind":"hyUnitComInfo.zhuceziben",'
                         '"type":"outputtext","format":"#0.00","dataOptions":"{'
                         'format:_EpSingleQuotes_#0.00_EpSingleQuotes_}"},{"id":"currency",'
                         '"bind":"hyUnitComInfo.currency","type":"outputtext","code":"金额币种代码","dataOptions":"{'
                         'code:_EpSingleQuotes_金额币种代码_EpSingleQuotes_}"},{"id":"yingyeqixianfrom",'
                         '"bind":"hyUnitComInfo.yingyeqixianfrom","type":"outputtext","format":"yyyy-MM-dd",'
                         '"dataOptions":"{format:_EpSingleQuotes_yyyy-MM-dd_EpSingleQuotes_}"},'
                         '{"id":"yingyeqixianto","bind":"hyUnitComInfo.yingyeqixianto","type":"outputtext",'
                         '"format":"yyyy-MM-dd ","dataOptions":"{format:_EpSingleQuotes_yyyy-MM-dd '
                         '_EpSingleQuotes_}"},{"id":"dengjijiguan","bind":"hyUnitComInfo.dengjijiguan",'
                         '"type":"outputtext"},{"id":"jinyingfanwei","bind":"hyUnitComInfo.jinyingfanwei",'
                         '"type":"outputtext"},{"id":"anquanxukezhennum","bind":"dataBean.anquanxukezhennum",'
                         '"type":"outputtext"},{"id":"zhuyaofuzerenname","bind":"dataBean.zhuyaofuzerenname",'
                         '"type":"outputtext"},{"id":"xukefanwei","bind":"dataBean.xukefanwei","type":"outputtext"},'
                         '{"id":"xukefazhengjiguan","bind":"dataBean.xukefazhengjiguan","type":"outputtext"},'
                         '{"id":"fazhengdate","bind":"dataBean.fazhengdate","type":"outputtext",'
                         '"format":"yyyy-MM-dd","dataOptions":"{format:_EpSingleQuotes_yyyy-MM-dd_EpSingleQuotes_}"},'
                         '{"id":"fazhengend","bind":"dataBean.fazhengend","type":"outputtext","format":"yyyy-MM-dd",'
                         '"dataOptions":"{format:_EpSingleQuotes_yyyy-MM-dd_EpSingleQuotes_}"},{"id":"companydes",'
                         '"bind":"hyUnitComInfo.companydes","type":"outputtext"},{"id":"pageScript1",'
                         '"bind":"pageScript","type":"output"},{"id":"_common_hidden_viewdata","type":"hidden",'
                         '"value":""}] '
        }
        cookies = ''
        for k, v in vv.cookies.get_dict().items():
            cookie_jar.set(k, v)
            cookies += '%s=%s; ' % (k, v)
        kk = 'http://218.60.149.226/PSPFrame/huiyuaninfomis2/backend/shigonginfoShiGongInfo_Detail_Read?ViewType=2' \
             '&DanWeiType=13&DanWeiGuid=%s&CurrentDanWeiGuid=%s' % (
                 danweiguid, danweiguid)
        bb = requests.post(url=uu, data=data,
                           headers={
                               'CSRFCOOKIE': vv.cookies.get_dict()['_CSRFCOOKIE'],
                               'Cookie': cookies,
                               'Referer': kk,
                           },

                           )

        company_zz = json.loads(bb.text)
        LN_data = {'name': '', 'taxID': '', 'address': '', 'tel': '', 'openingBank': '',
                   'bankAccounts': '', 'tokenKey': token
                   }
        company_name = company_zz['controls'][0]['value']
        LN_data['name'] = company_name
        bank = company_zz['controls'][13]['value']

        if len(bank) != 0:
            LN_data['openingBank'] = bank.split()[0]
        bank_number = company_zz['controls'][14]['value']

        if len(bank_number) != 0:
            LN_data['bankAccounts'] = bank_number.split()[0]

        localmobile = company_zz['controls'][16]['value']
        if len(localmobile) != 0:
            LN_data['tel'] = localmobile.split()[0]

        address = company_zz['controls'][20]['value']
        if len(address) != 0:
            LN_data['address'] = address.split()[0]

        print(LN_data)
        # xx = requests.post(url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyInvoice.htm',
        #                    data=LN_data
        #                    )
        # handle(xx)


def handle(xx):
    print(xx.text)


start()
