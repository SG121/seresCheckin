import os,sys,json,logging,time,random,uuid

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

def randomConfig(config):
    if 'baseData' not in config:
        logger.info('生成随机配置')
        systemVersion = ['8','9','10','11']
        resolution = ['2400*1080','2240*1080','1920*1080']
        config['baseData'] = {
            '_platform': '2',
            '_systemVersion': random.choice(systemVersion),
            '_resolution': random.choice(resolution),
            '_version': '3.2.2',
            '_uuid': uuid.uuid1().hex
        }
    if 'notify' not in config:
        config["notify"] = {
            "BARK": "",
            "SCKEY": "",
            "TG_BOT_TOKEN": "",
            "TG_USER_ID": "",
            "TG_PROXY_IP": "",
            "TG_PROXY_PORT": "",
            "DD_BOT_ACCESS_TOKEN": "",
            "DD_BOT_SECRET": "",
            "QYWX_APP": ""
        }
    if 'draw' not in config:
        config['draw'] = False
    if '_version' in config['baseData']:
        config['baseData']['_version'] = '3.2.2'
    with open("config.json", "w") as fp:
        fp.write(json.dumps(config,indent=4))
    return config

rootDir = os.path.dirname(os.path.abspath(__file__))
configPath = rootDir + "/config.json"
config = readConfig(configPath)
logDir = rootDir + "/logs/"
if ('logDir' in config) and (config['logDir'] != ''):
    logDir = config['logDir'] + "/serseCheckin"
logger = createLog(logDir)
config = randomConfig(config)