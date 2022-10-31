#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from requests.utils import dict_from_cookiejar
from lxml import etree
from hit.ids.login import idslogin
from hit.exceptions import LoginFailed
import json
from urllib import parse
from json import loads
import re
import ddddocr
import datetime
import argparse
import urllib
from _datetime import date
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header

parser = argparse.ArgumentParser(description='HIT疫情上报')
parser.add_argument('username', help='统一身份认证登录用户名（学号）')
parser.add_argument('password', help='统一身份认证登录密码')
parser.add_argument('location', help='上报地址')
parser.add_argument('-k', '--api_key', help='Server酱的SCKEY，或是电邮密码/Key')
parser.add_argument('-m', '--mail_to', help='电邮信息，格式"服务器[:端口[U]]:用户名"')


def print_log(msg: str) -> None:
    print(f'[{datetime.datetime.now()}] {msg}')


def get_report_info(location_name: str, token: str, code:str) -> dict:
    with open('post_data.jsonc', 'r', encoding='utf-8') as jsonfile:
        jsondata = ''.join(
            line for line in jsonfile if not line.startswith('//'))
    model = json.loads(re.sub("//.*", "", jsondata, flags=re.MULTILINE))
    geo_api_url = 'https://restapi.amap.com/v3/geocode/geo?key=be8762efdce0ddfbb9e2165a7cc776bd&s=rsv3&language=zh_cn&extensions=base&appname=https%3A%2F%2Fxg.hit.edu.cn%2Fzhxy-xgzs%2Fxg_mobile%2FxsMrsbNew&csid=47204181-378A-4F55-A94D-548A5BFD0DFD&sdkversion=1.4.16&address='
    regeo_api_url = 'https://restapi.amap.com/v3/geocode/regeo?key=be8762efdce0ddfbb9e2165a7cc776bd&s=rsv3&language=zh_cn&extensions=base&appname=https%3A%2F%2Fxg.hit.edu.cn%2Fzhxy-xgzs%2Fxg_mobile%2FxsMrsbNew&csid=47204181-378A-4F55-A94D-548A5BFD0DFD&sdkversion=1.4.16&location='
    addr = location_name
    addr = parse.quote(addr)
    geo_response = requests.get(geo_api_url+addr)
    location = geo_response.json()['geocodes'][0]['location']
    addr_spl = location.split(',')
    longitude, latitude = addr_spl[0], addr_spl[1]
    regeo_response = requests.get(regeo_api_url+location)
    geo_info = regeo_response.json()['regeocode']
    addr = geo_info['formatted_address']
    addr_component = geo_info['addressComponent']
    province = addr_component['province']
    city = addr_component['city']
    district = addr_component['district']
    street_number = addr_component['streetNumber']
    street_number = street_number['street']+street_number['number']
    model['gpsjd'] = float(longitude)
    model['gpswd'] = float(latitude)
    model['kzl6'] = province
    model['kzl7'] = city
    model['kzl8'] = district
    model['kzl9'] = street_number
    model['kzl10'] = addr
    model['kzl38'] = province
    model['kzl39'] = city
    model['kzl40'] = district
    model['yzm'] = code
    report_info = {
        'info': json.dumps({'model': model, 'token': token})
    }
    print_log('生成上报信息成功')
    # print_log(report_info)
    return report_info


def main(args):
    print_log('尝试登录...')
    lose_count = 0
    s = None
    while lose_count < 10 and s == None:
        try:
            s = idslogin(args.username, args.password)
            break
        except LoginFailed as e:
            print_log(f'登录失败:{e}')
            lose_count += 1
    if lose_count == 10:
        return False, '登录失败'

    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A403 NetType/WIFI Language/zh_CN HuaWei-AnyOffice/1.0.0/cn.edu.hit.welink',
        'Referer': 'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/edit'
    })
    r = s.get('https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/shsj/common')
    _ = urllib.parse.urlparse(r.url)
    if _.hostname != 'xg.hit.edu.cn':
        print_log('登录失败')
        return False, '登录失败'
    print_log('登录成功')
    getmrsb_url='https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/getMrsb'
    todaydata_url='https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/checkTodayData'
    jkdy_url= 'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/checkMrsbJkdy'#post empty
    token_url = 'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xs/getToken'

    code_url = 'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/shsj/code'
    

    prefix_tasks=[todaydata_url,getmrsb_url,jkdy_url]

    response = s.post(token_url)
    print_log(f'POST {token_url} {response.status_code}')
    token = str(response.content)[2:-1]
    for task in prefix_tasks:
        task_resp=s.post(task)
        print_log(f'POST {task} {task_resp.status_code}')
    save_url = 'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsMrsbNew/save'
    print_log(f'尝试无验证码上报......')
    report_info = get_report_info(args.location, token, '')
    response = s.post(save_url, data=report_info)
    print_log(f'POST {save_url} {response.status_code}')
    print(response.json())
    is_success=response.json()['isSuccess']
    if is_success:
        return is_success, '提交成功'
    print_log(f'无验证码上报失败；尝试有验证码上报......')
    response = requests.get(code_url) # 验证码
    print_log(f'GET {code_url} {response.status_code}')
    ocr = ddddocr.DdddOcr()
    code_ocr = ocr.classification(response.content)
    print_log(f'Captcha: {code_ocr}')
    report_info = get_report_info(args.location, token, code_ocr)
    response = s.post(save_url, data=report_info)
    print_log(f'POST {save_url} {response.status_code}')
    print(response.json())
    is_success=response.json()['isSuccess']
    res_msg = '提交成功' if is_success else '提交失败'
    return is_success, res_msg


if __name__ == '__main__':
    args = parser.parse_args()
    is_successful, msg = main(args)
    print_log(msg)
    if args.api_key:
        report_msg = ""  # 生成上报报告
        if is_successful:
            report_msg = f"疫情上报成功！{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            report_msg = f"疫情上报失败，原因：{msg}{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"

        if args.mail_to:
            mail_info = args.mail_to.split(':')
            mail_addr = mail_info[-1]

            msg = MIMEText(report_msg, 'plain', 'utf-8')
            msg['Subject'] = Header(report_msg, 'utf-8')
            msg['From'] = 'AUTO_REPORT_BOT'
            msg['To'] = mail_addr
            print_log('尝试发送邮件...')

            host = mail_info[0]
            unsafe = False
            if len(mail_info) == 3 and mail_info[1][-1] == 'U':
                unsafe = True
                mail_info[1] = mail_info[1][:-1]
            try:
                s = smtplib.SMTP(host=host) if len(mail_info) == 2 else smtplib.SMTP(
                    host=host, port=int(mail_info[1]))
                print_log(mail_info)
                s.ehlo_or_helo_if_needed()
                if not unsafe:
                    s.starttls()
                s.login(mail_addr, args.api_key)
                print_log('邮件服务器连接成功')
                s.ehlo_or_helo_if_needed()
                s.sendmail(mail_addr, mail_addr, msg.as_string())
                s.quit()
                print_log('邮件发送成功！')
            except Exception as e:
                print_log('邮件发送失败。')
                print_log(e)

        else:
            print_log('发送微信提醒...')
            requests.get(
                f"https://sc.ftqq.com/{args.api_key}.send?text={report_msg}")
