# Author: leeyiding(乌拉)
# Date: 2020-08-12
# Link: 
# Version: 0.0.2
# UpdateDate: 2020-08-12 16:03
# UpdateLog: 领取在线10分钟奖励 1积分

import requests
import json
import os
import sys
import logging
import time

def postApi(cookie,option,function):
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'okhttp-okgo/jeasonlzy',
        'APPACCESSTOKEN': cookie,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '106',
        'Host': 'app.seres.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    data = {
        '_platform': '2',
        '_systemVersion': '11',
        '_resolution': '2261*1080',
        '_version': '2.6.1',
        '_uuid': '2f10ec91651f435b182296d44f0621027'
    }
    response = requests.post('https://app.seres.cn/api/user/app/{}/{}'.format(option,function), headers=headers, data=data)
    return response.json()

def readConfig(configPath):
    if not os.path.exists(configPath):
        print('配置文件不存在，请复制模板文件config.sample.json为config.json')
        sys.exit(1)
    with open(configPath,encoding='UTF-8') as fp:
        try:
            config = json.load(fp)
            return config
        except:
            print('读取配置文件失败，请检查配置文件是否符合json语法')
            sys.exit(1)

def createLog(logDir):
    # 日志输出控制台
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # 日志输入文件
    date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
    logPath = '{}/{}.log'.format(logDir,date)
    if not os.path.exists(logDir):
        logger.warning("未检测到日志目录存在，开始创建logs目录")
        os.makedirs(logDir)
    fh = logging.FileHandler(logPath, mode='a', encoding='utf-8')
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)
    return logger

def cleanLog(logDir):
    logger.info("开始清理日志")
    cleanNum = 0
    files = os.listdir(logDir)
    for file in files:
        today = time.mktime(time.strptime(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()),"%Y-%m-%d-%H-%M-%S"))
        logDate = time.mktime(time.strptime(file.split(".")[0],"%Y-%m-%d-%H-%M-%S"))
        dayNum = int((int(today) - int(logDate)) / (24 * 60 * 60))
        if dayNum > 7:
            os.remove("{}/{}".format(logDir,file))
            cleanNum += 1
            logger.info("已删除{}天前日志{}".format(dayNum,file))
    if cleanNum == 0:
        logger.info("未检测到过期日志，无需清理！")

rootDir = os.path.dirname(os.path.abspath(__file__))
configPath = rootDir + "/config.json"
config = readConfig(configPath)
logDir = rootDir + "/logs/"
if ('logDir' in config) and (config['logDir'] != ''):
    logDir = config['logDir'] + "/serseCheckin"
logger = createLog(logDir)
userNum = len(config['cookie'])
logger.info('共{}个账号'.format(userNum))

for i in range(userNum):
    # 检查签到状态
    logger.info('账号开始{}登陆'.format(i+1))
    cookie = config['cookie'][i]
    userInfo = postApi(cookie,'me','get-me-center-data')
    if userInfo['code'] == '4001':
        logger.error('用户{} Cookie无效'.format(i+1))
        continue
    else:
        logger.info('登陆成功')
    nickname = userInfo['value']['nickname']
    # 签到 1积分
    if userInfo['value']['todayCheckedIn'] == True:
        logger.info('用户【{}】今日已签到，无需重复签到'.format(nickname))
    else:
        logger.info('用户【{}】今日未签到，开始签到'.format(nickname))
        checkinResult = postApi(cookie,'me','checkin')
        logger.info(checkinResult['message'])
    # 领取在线10分钟奖励 1积分
    logger.info('领取在线10分钟奖励')
    awardResult = postApi(cookie, 'point', 'add-for-using-10min')
    if awardResult['value']['amount'] == 1:
        logger.info('获得1积分')
    elif awardResult['value']['amount'] == 0:
        logger.info('今日已领取过奖励')

cleanLog(logDir)
    
    