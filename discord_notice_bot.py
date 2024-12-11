# TestServer 채널 운영 (테스트용)
# undetected-chromedriver 3.0.6 버전
# selenium 4.9 버전

import chromedriver_autoinstaller
import random
import copy
import asyncio
from user_agents import parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from discord.ext import commands, tasks
import discord

chromedriver_autoinstaller.install()

# ========================================== config.json ===========================================
import json

# config.json 파일 로드
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()


# ========================================== 변수 ===================================================
# discord_token : 디스코드 토큰
# channel_id : 디스코드 채널 아이디
# local_computer_user_agent_txt_path : user-agent 15000개 데이터 txt파일이 저장된 공간 (local)
# GCP_server_computer_user_agent_txt_path : user-agent 15000개 데이터 txt파일이 저장된 공간 (GCP server)
# chromedriver_path : chromedriver 경로
before_subjects = [[] for _ in range(14)] # 14개의 2차원 빈 배열 초기화 [홈페이지 번째수][(게시글 제목, 게시글 url)]
cur_subjects = [[] for _ in range(14)]  # 14개의 2차원 빈 배열 초기화 [홈페이지 번째수][(게시글 제목, 게시글 url)]
homepage_num = 0 # 현재 보고 있는 홈페이지 (0번이면 새소식 페이지 index)
attempt = 1 # 전체 공지 순회 횟수
# 공지 모니터링할 성결대학교 홈페이지 URL 
sku_site_links = ['https://www.sungkyul.ac.kr/skukr/342/subview.do', # 새소식 (0)
            'https://www.sungkyul.ac.kr/skukr/343/subview.do', # 학사 (1)
            'https://www.sungkyul.ac.kr/skukr/901/subview.do', # 학생 (2)
            'https://www.sungkyul.ac.kr/skukr/344/subview.do', # 장학/등록/학자금 (3)
            'https://www.sungkyul.ac.kr/skukr/345/subview.do', # 입학 (4)
            'https://www.sungkyul.ac.kr/skukr/346/subview.do', # 취업/진로개발/창업 (5)
            'https://www.sungkyul.ac.kr/skukr/347/subview.do', # 공모/행사 (6)
            'https://www.sungkyul.ac.kr/skukr/348/subview.do', # 교육/글로벌 (7)
            'https://www.sungkyul.ac.kr/skukr/349/subview.do', # 일반 (8)
            'https://www.sungkyul.ac.kr/skukr/350/subview.do', # 입찰구매정보 (9)
            'https://www.sungkyul.ac.kr/skukr/351/subview.do', # 사회봉사센터 (10)
            'https://www.sungkyul.ac.kr/skukr/352/subview.do', # 장애학생지원센터 (11)
            'https://www.sungkyul.ac.kr/skukr/353/subview.do', # 생활관 (12)
            'https://www.sungkyul.ac.kr/skukr/354/subview.do', # 비교과 (13)
            ]

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), heartbeat_timeout=60)
channel = None  # 채널 변수를 전역 변수로 설정

# ========================================== 함수 ===================================================
def make_user_agent(ua, is_mobile): 
    user_agent = parse(ua)
    model = user_agent.device.model
    platform = user_agent.os.family
    platform_version = user_agent.os.version_string + ".0.0"
    version = user_agent.browser.version[0]
    ua_full_version = user_agent.browser.version_string
    architecture = "x86"
    if is_mobile:
        platform_info = "Linux armv8l"
        architecture= ""
    else:
        platform_info = "Win32"
        model = ""
    RET_USER_AGENT = {
        "appVersion" : ua.replace("Mozilla/", ""),
        "userAgent": ua,
        "platform" : f"{platform_info}",
        "acceptLanguage" : "ko-KR, kr, en-US, en",
        "userAgentMetadata":{
            "brands" : [
                {"brand":"Google Chrome", "version":f"{version}"},
                {"brand":"Chromium", "version":f"{version}"},
                {"brand":"Not A;Brand", "version":"99"},
            ],
            "fullVersionList":[
                {"brand":"Google Chrome", "version":f"{version}"},
                {"brand":"Chromium", "version":f"{version}"},
                {"brand":"Not A;Brand", "version":"99"},
            ],
            "fullVersion":f"{ua_full_version}",
            "platform" :platform,
            "platformVersion":platform_version,
            "architecture":architecture,
            "model" : model,
            "mobile":is_mobile
        }
    }
    return RET_USER_AGENT

def read_agents():
    agents = []
    f = open(config['local_computer_user_agent_txt_path'],"r",encoding="utf8")
    while True:
        line = f.readline()
        if not line:
            break
        agents.append(line.rstrip())
    return agents

def make_driver():
    try:
        pc_device = ["1920,1440","1920,1200","1920,1080","1600,1200","1600,900",
                        "1536,864", "1440,1080","1440,900","1360,768"
                ]

        mo_device = [
                    "360,640", "360,740", "375,667", "375,812", "412,732", "412,846",
                    "412,869", "412,892", "412,915"
                ]

        width,height = random.choice(mo_device).split(",")
        UA_list = read_agents()
        UA = random.choice(UA_list)
        print("여기까지완료1")
        options = uc.ChromeOptions()
        options.add_argument(f'--user-agent={UA}')
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
        options.add_argument('--disable-logging')
        options.add_argument('--disable-popup-blocking')
        # linux 환경에서 필요한 option
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        print("여기까지완료2")
        driver = uc.Chrome(executable_path=config['chromedriver_path'],options=options) # Linux chromedriver 경로 : /home/hhs0991/chromedriver-linux64/chromedriver
        print("여기까지완료3")
        UA_Data = make_user_agent(UA, True)
        print("여기까지완료4")
        driver.execute_cdp_cmd("Network.setUserAgentOverride", UA_Data)
        print("여기까지완료5")

        Mobile = {"enabled":True, "maxTouchPoints" : random.choice([1,5])}
        driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", Mobile)
        driver.execute_cdp_cmd("Emulation.setNavigatorOverrides",{"platform":"Linux armv8l"})

        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width":int(width),
            "height":int(height),
            "deviceScaleFactor":1,
            "mobile":True,
        })

        def generate_random_geolcation():
            ltop_lat = 37.61725745260699
            ltop_long = 126.92437164480178
            rbottom_lat = 37.56825361755575
            rbottom_long = 127.05771697149082

            targetLat = random.uniform(rbottom_lat, ltop_lat)
            targetLong = random.uniform(ltop_long, rbottom_long)
            return {"latitude" : targetLat, "longitude" : targetLong, "accuracy":100}
        
        GEO_DATA = generate_random_geolcation()
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", GEO_DATA)
        print("여기까지완료6")
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride",UA_Data)
        driver.set_window_size(int(width),int(height))
        print("여기까지완료7")
        return driver
        
    except Exception as e:
        print(e)
        driver = None
        return driver

driver = make_driver()

print("==================================================")
print(driver)
print("==================================================")
# ========================================== 봇 이벤트 및 명령어 ====================================

@bot.event
async def on_ready():
    global channel  # 채널 변수를 전역 변수로 설정
    print(f'Login bot: {bot.user}')
    channel = bot.get_channel(config['channel_id'])  # 채널 ID를 이용하여 채널 변수 설정
    # if(driver == None):
    #     await channel.send(f'driver 없음')
    check_notices.start()

@tasks.loop(minutes=15) 
async def check_notices():
    global homepage_num
    global attempt

    print(f"{attempt}번째 시도 중입니다.")

    for sku_site_link in sku_site_links:
        try:
            driver.get(sku_site_link)
        except Exception as e:
            print(f"[ERROR 001] 성결대학교 홈페이지 오류입니다. {sku_site_link} 페이지를 띄우지 못했습니다.")
            print(f"에러명은 아래와 같음")
            print(f"{e}")
            #await channel.send(f'채팅 서버 개발자님 확인해 주세요! 봇이 너무 아파요 ㅜ_ㅜ \n 에러 코드 : [ERROR 001] 성결대학교 홈페이지 오류입니다. {sku_site_link} 페이지를 확인하지 못했습니다. \n 곧 채팅 서버 관리자가 나타나서 밤샘 작업을 하여 정상화할 예정이에요. 이용에 불편을 드려서 죄송합니다.')

        driver.implicitly_wait(200)

        try:
            post_elements = driver.find_elements(By.CSS_SELECTOR, '.td-subject > a')
        except:
            print("[ERROR 002] 성결대학교 상위 10개 공지 전체 element CSS_SELECTOR 오류입니다.")
            #await channel.send(f'채팅 서버 개발자님 확인해 주세요! 봇이 너무 아파요 ㅜ_ㅜ \n [ERROR 002] 성결대학교 상위 10개 공지 전체 element CSS_SELECTOR 오류입니다. \n 곧 채팅 서버 관리자가 나타나서 밤샘 작업을 하여 정상화할 예정이에요. 이용에 불편을 드려서 죄송합니다.')

        try:
            for post_element in post_elements:
                url = post_element.get_attribute('href')
                subject_element = post_element.find_element(By.CSS_SELECTOR, 'strong')
                subject = subject_element.text
                cur_subjects[homepage_num].append((subject, url))
        except:
            print("[ERROR 003] 성결대학교 게시물의 제목이나 URL을 받아오지 못했습니다.")
            #await channel.send(f'채팅 서버 개발자님 확인해 주세요! 봇이 너무 아파요 ㅜ_ㅜ \n [ERROR 003] 성결대학교 게시물의 제목이나 URL을 받아오지 못했습니다. \n 곧 채팅 서버 관리자가 나타나서 밤샘 작업을 하여 정상화할 예정이에요. 이용에 불편을 드려서 죄송합니다.')

        if attempt != 1 and cur_subjects[homepage_num] != before_subjects[homepage_num]:
            for subject,url in cur_subjects[homepage_num]:
                if (subject, url) not in before_subjects[homepage_num]:
                    print(f"새로운 공지 제목 : {subject}")
                    print(f"새로운 공지 URL : {url.strip()}")
                    await channel.send(f'새로운 공지 제목 : {subject} \n {url.strip()}')

        before_subjects[homepage_num] = copy.deepcopy(cur_subjects[homepage_num])
        cur_subjects[homepage_num].clear()
        
        homepage_num += 1
        if(homepage_num == 14):
            homepage_num -= 14

        await asyncio.sleep(random.uniform(5.0, 10.0))

    attempt += 1

bot.run(config['discord_token'])