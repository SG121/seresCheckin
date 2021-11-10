#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# 通知服务修改自https://raw.githubusercontent.com/whyour/hundun/master/quanx/util.py

import sys
import os
cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(cur_path)[0]
sys.path.append(root_path)
import requests
import json
import traceback
import time
import hmac
import hashlib
import base64
import urllib.parse
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
from utils import config,logger

# 通知服务
BARK = ''                                                                 # bark服务,此参数如果以http或者https开头则判定为自建bark服务; secrets可填;
SCKEY = ''                                                                # Server酱的SCKEY; secrets可填
TG_BOT_TOKEN = ''                                                         # tg机器人的TG_BOT_TOKEN; secrets可填
TG_USER_ID = ''                                                           # tg机器人的TG_USER_ID; secrets可填
TG_PROXY_IP = ''                                                          # tg机器人的TG_PROXY_IP; secrets可填
TG_PROXY_PORT = ''                                                        # tg机器人的TG_PROXY_PORT; secrets可填
DD_BOT_ACCESS_TOKEN = ''                                                  # 钉钉机器人的DD_BOT_ACCESS_TOKEN; secrets可填
DD_BOT_SECRET = ''                                                        # 钉钉机器人的DD_BOT_SECRET; secrets可填
QYWX_APP = ''                                                             # 企业微信应用的QYWX_APP; secrets可填 参考http://note.youdao.com/s/HMiudGkb

notify_mode = []

if "BARK" in config['notify'] and config['notify']["BARK"]:
    BARK = config['notify']["BARK"]
if "SCKEY" in config['notify'] and config['notify']["SCKEY"]:
    SCKEY = config['notify']["SCKEY"]
if "TG_BOT_TOKEN" in config['notify'] and config['notify']["TG_BOT_TOKEN"] and "TG_USER_ID" in config['notify'] and config['notify']["TG_USER_ID"]:
    TG_BOT_TOKEN = config['notify']["TG_BOT_TOKEN"]
    TG_USER_ID = config['notify']["TG_USER_ID"]
if "DD_BOT_ACCESS_TOKEN" in config['notify'] and config['notify']["DD_BOT_ACCESS_TOKEN"] and "DD_BOT_SECRET" in config['notify'] and config['notify']["DD_BOT_SECRET"]:
    DD_BOT_ACCESS_TOKEN = config['notify']["DD_BOT_ACCESS_TOKEN"]
    DD_BOT_SECRET = config['notify']["DD_BOT_SECRET"]
if "QYWX_APP" in config['notify'] and config['notify']["QYWX_APP"]:
    QYWX_APP = config['notify']["QYWX_APP"]

if BARK:
    notify_mode.append('bark')
    logger.info("BARK 推送打开")
if SCKEY:
    notify_mode.append('sc_key')
    logger.info("Server酱 推送打开")
if TG_BOT_TOKEN and TG_USER_ID:
    notify_mode.append('telegram_bot')
    logger.info("Telegram 推送打开")
if DD_BOT_ACCESS_TOKEN and DD_BOT_SECRET:
    notify_mode.append('dingding_bot')
    logger.info("钉钉机器人 推送打开")
if QYWX_APP:
    notify_mode.append('qywxapp_bot')
    logger.info("企业微信应用 推送打开")

def bark(title, content):
    if not BARK:
        logger.error("bark服务的bark_token未设置!!\n取消推送")
        return
    logger.info("bark服务启动")
    url = None
    if BARK.startswith('http'):
      url = f"""{BARK}/{title}/{content}"""
    else:
      url = f"""https://api.day.app/{BARK}/{title}/{content}"""
    response = requests.get(url).json()
    if response['code'] == 200:
        logger.info('推送成功！')
    else:
        logger.error('推送失败！')

def serverJ(title, content):
    if not SCKEY:
        logger.error("server酱服务的SCKEY未设置!!\n取消推送")
        return
    logger.info("serverJ服务启动")
    data = {
        "text": title,
        "desp": content.replace("\n", "\n\n")
    }
    response = requests.post(f"https://sc.ftqq.com/{SCKEY}.send", data=data).json()
    if response['errno'] == 0:
        logger.info('推送成功！')
    else:
        logger.error('推送失败！')

def telegram_bot(title, content):
    bot_token = TG_BOT_TOKEN
    user_id = TG_USER_ID
    if not bot_token or not user_id:
        logger.error("tg服务的bot_token或者user_id未设置!!\n取消推送")
        return
    logger.info("tg服务启动")
    url=f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'chat_id': str(TG_USER_ID), 'text': f'{title}\n\n{content}', 'disable_web_page_preview': 'true'}
    proxies = None
    if TG_PROXY_IP and TG_PROXY_PORT:
        proxyStr = "http://{}:{}".format(TG_PROXY_IP, TG_PROXY_PORT)
        proxies = {"http": proxyStr, "https": proxyStr}
    response = requests.post(url=url, headers=headers, params=payload, proxies=proxies).json()
    if response['ok']:
        logger.info('推送成功！')
    else:
        logger.error('推送失败！')

def dingding_bot(title, content):
    timestamp = str(round(time.time() * 1000))  # 时间戳
    secret_enc = DD_BOT_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DD_BOT_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
    logger.info('开始使用 钉钉机器人 推送消息...', end='')
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_ACCESS_TOKEN}&timestamp={timestamp}&sign={sign}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        'msgtype': 'text',
        'text': {'content': f'{title}\n\n{content}'}
    }
    response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=15).json()
    if not response['errcode']:
        logger.info('推送成功！')
    else:
        logger.error('推送失败！')

def qywxapp_bot(title, content):
    if not QYWX_APP:
        logger.error("企业微信应用的QYWX_APP未设置!!\n取消推送")
        return
    logger.info("企业微信应用启动")
    qywx_app_params = QYWX_APP.split(',')
    url='https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    headers= {
        'Content-Type': 'application/json',
    }
    payload = {
        'corpid': qywx_app_params[0],
        'corpsecret': qywx_app_params[1],
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(payload), timeout=15).json()
    accesstoken = response["access_token"]
    html = content.replace("\n", "<br/>")

    options = None
    if not qywx_app_params[4]:
        options = {
            'msgtype': 'text',
            'text': {
                content: f'{title}\n\n${content}'
            }
        }
    elif qywx_app_params[4] == '0':
        options = {
            'msgtype': 'textcard',
            'textcard': {
                'title': f'{title}',
                'description': f'{content}',
                'btntxt': '更多'
            }
        }
    elif qywx_app_params[4] == '1':
        options = {
            'msgtype': 'text',
            'text': {
                content: f'{title}\n\n${content}'
            }
        }
    else:
        options = {
            'msgtype': 'mpnews',
            'mpnews': {
                'articles': [
                    {
                        'title': f'{title}',
                        'thumb_media_id': f'{qywx_app_params[4]}',
                        'author': '智能助手',
                        'content_source_url': '',
                        'content': f'{html}',
                        'digest': f'{content}'
                    }
                ]
            }
        }

    url=f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={accesstoken}"
    data = {
        'touser': f'{change_user_id(content)}',
        'agentid': f'{qywx_app_params[3]}',
        'safe': '0'
    }
    data.update(options)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()

    if response['errcode'] == 0:
        logger.info('推送成功！')
    else:
        logger.error('推送失败！')

def change_user_id(desp):
    qywx_app_params = QYWX_APP.split(',')
    if qywx_app_params[2]:
        userIdTmp = qywx_app_params[2].split("|")
        userId = ""
        for i in range(len(userIdTmp)):
            count1 = f"账号{i + 1}"
            count2 = f"签到号{i + 1}"
            if re.search(count1, desp) or re.search(count2, desp):
                userId = userIdTmp[i]
        if not userId:
            userId = qywx_app_params[2]
        return userId
    else:
        return "@all"

def send(title, content):
    """
    使用 bark, telegram bot, dingding bot, serverJ 发送手机推送
    :param title:
    :param content:
    :return:
    """
    for i in notify_mode:
        if i == 'bark':
            if BARK:
                bark(title=title, content=content)
            else:
                logger.error('未启用 bark')
            continue
        if i == 'sc_key':
            if SCKEY:
                serverJ(title=title, content=content)
            else:
                logger.error('未启用 Server酱')
            continue
        elif i == 'dingding_bot':
            if DD_BOT_ACCESS_TOKEN and DD_BOT_SECRET:
                dingding_bot(title=title, content=content)
            else:
                logger.error('未启用 钉钉机器人')
            continue
        elif i == 'telegram_bot':
            if TG_BOT_TOKEN and TG_USER_ID:
                telegram_bot(title=title, content=content)
            else:
                logger.error('未启用 telegram机器人')
            continue
        elif i == 'qywxapp_bot':
            if QYWX_APP:
                qywxapp_bot(title=title, content=content)
            else:
                logger.error('未启用 企业微信应用推送')
            continue
        else:
            logger.error('此类推送方式不存在')

def requests_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=frozenset(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])  # urllib3 默认对除 GET 以外的方法，不设置自动重试功能，所以要主动添加白名单
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def main():
    send('title', 'content')


if __name__ == '__main__':
    main()