# WARNING:discord.gateway:Shard ID None heartbeat blocked for more than N seconds. 오류 해결

# 안정화 버전 (stable version - 20240826)
# 실행 명령어 : pm2 start 20240826.py --interpreter python3

# --------------- 필 독 ------------------
# # 주의1 : 실행하고 종료한 경우
# 1) xvfb-run, Xvfb, chrome, undetected_chro, python3 제거하기
# 2) 인스턴스를 중지하고 다시 시작한다.
# --------------------------------------

# --------------- 호환 버전 확인 -------------
# undetected-chromedriver 3.5.5 버전 (pip show undetected-chromedriver)
# selenium 4.23.1 버전 (pip show selenium)

# Google Chrome 브라우저 버전 128.0.6613.84 (google-chrome --version)
# ChromeDriver 버전 128.0.6613.84 (cd chromedriver-linux64/ 후에 ./chromedriver --version)
# ---------------------------------------------
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from discord.ext import commands, tasks
import discord
import random
import copy
import chromedriver_autoinstaller

# chromedriver 자동 설치
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

before_subjects = [[] for _ in range(12)] # 12개의 2차원 빈 배열 초기화 [홈페이지 번째수][(게시글 제목, 게시글 url)]
cur_subjects = [[] for _ in range(12)]  # 12개의 2차원 빈 배열 초기화 [홈페이지 번째수][(게시글 제목, 게시글 url)]
homepage_num = 0 # 현재 보고 있는 홈페이지 (0번이면 새소식 페이지 index)
attempt = 1 # 전체 공지 순회 횟수

# 2024-07-14 수요자의 요구사항을 반영하여 # 입찰구매정보 (9), # 새소식 (0) 은 공지 서비스를 진행하지 않는다.
# 공지 모니터링할 성결대학교 홈페이지 URL 
sku_site_links = [
            'https://www.sungkyul.ac.kr/skukr/343/subview.do', # 학사 (0)
            'https://www.sungkyul.ac.kr/skukr/901/subview.do', # 학생 (1)
            'https://www.sungkyul.ac.kr/skukr/344/subview.do', # 장학/등록/학자금 (2)
            'https://www.sungkyul.ac.kr/skukr/345/subview.do', # 입학 (3)
            'https://www.sungkyul.ac.kr/skukr/346/subview.do', # 취업/진로개발/창업 (4)
            'https://www.sungkyul.ac.kr/skukr/347/subview.do', # 공모/행사 (5)
            'https://www.sungkyul.ac.kr/skukr/348/subview.do', # 교육/글로벌 (6)
            'https://www.sungkyul.ac.kr/skukr/349/subview.do', # 일반 (7)
            'https://www.sungkyul.ac.kr/skukr/351/subview.do', # 사회봉사센터 (8)
            'https://www.sungkyul.ac.kr/skukr/352/subview.do', # 장애학생지원센터 (9)
            'https://www.sungkyul.ac.kr/skukr/353/subview.do', # 생활관 (10)
            'https://www.sungkyul.ac.kr/skukr/354/subview.do', # 비교과 (11)
            ]

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), heartbeat_timeout=60)
channel = None  # 채널 변수를 전역 변수로 설정

# ========================================== 함수 ===================================================
def make_user_agent(ua, is_mobile): 
    from user_agents import parse
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
    f = open(config['GCP_server_computer_user_agent_txt_path'],"r",encoding="utf8")
    while True:
        line = f.readline()
        if not line:
            break
        agents.append(line.rstrip())
    return agents

def make_driver():
    try:
        pc_device = ["1920,1440","1920,1200","1920,1080","1600,1200","1600,900",
                     "1536,864", "1440,1080","1440,900","1360,768"]
        mo_device = ["360,640", "360,740", "375,667", "375,812", "412,732", "412,846",
                     "412,869", "412,892", "412,915"]
        width, height = random.choice(mo_device).split(",")
        UA_list = read_agents()
        UA = random.choice(UA_list)
        options = uc.ChromeOptions()
        options.add_argument(f'--user-agent={UA}')
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
        options.add_argument('--disable-logging')
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(executable_path=config['chromedriver_path'], options=options)
        UA_Data = make_user_agent(UA, True)
        driver.execute_cdp_cmd("Network.setUserAgentOverride", UA_Data)
        Mobile = {"enabled":True, "maxTouchPoints" : random.choice([1,5])}
        driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", Mobile)
        driver.execute_cdp_cmd("Emulation.setNavigatorOverrides", {"platform":"Linux armv8l"})
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width":int(width),
            "height":int(height),
            "deviceScaleFactor":1,
            "mobile":True,
        })
        GEO_DATA = {"latitude": random.uniform(37.56825361755575, 37.61725745260699),
                    "longitude": random.uniform(126.92437164480178, 127.05771697149082),
                    "accuracy":100}
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", GEO_DATA)
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride", UA_Data)
        driver.set_window_size(int(width), int(height))
        return driver
    except Exception as e:
        print(f"Driver 생성 중 오류 발생: {e}")
        return None

async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_page(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    for post in soup.select('.td-subject > a'):
        url = post.get('href')
        subject = post.select_one('strong').text
        
        if url:
            # URL이 상대 경로일 경우 base_url과 결합
            if not url.startswith('http'):
                # base_url의 끝에 있는 슬래시를 제거하고, 상대 URL의 시작에 있는 슬래시를 제거합니다.
                # ex)  https://www.sungkyul.ac.kr/skukr/354/
                # ->   https://www.sungkyul.ac.kr/skukr/354로 변환
                url = base_url+url
        
        posts.append((subject, url))
    return posts

# ========================================== 봇 이벤트 및 명령어 ====================================

@bot.event
async def on_ready():
    global channel  # 채널 변수를 전역 변수로 설정
    print(f'Login bot: {bot.user}')
    channel = bot.get_channel(config['channel_id'])  # 채널 ID를 이용하여 채널 변수 설정
    # if driver is None:
    #     await channel.send(f'시작 시 driver 없음')
    check_notices.start()

@tasks.loop(minutes=15) 
async def check_notices():
    global homepage_num
    global attempt
    # if driver is None: # 임시
    #     await channel.send(f'실행 중간 driver 없음') # 임시

    print(f"{attempt}번째 시도 중입니다.")
    # await channel.send(f"{attempt}번째 시도 중입니다.") # 임시

    async with aiohttp.ClientSession() as session:
        for sku_site_link in sku_site_links:
            try:
                html = await fetch_page(session, sku_site_link)
                base_url = "https://www.sungkyul.ac.kr" # 기본 URL을 생성
                posts = await parse_page(html, base_url)
                cur_subjects[homepage_num] = posts
            except Exception as e:
                print(f"[ERROR] 페이지 처리 중 오류 발생: {e}")

            different_subject_cnt = 0
            if attempt != 1 and cur_subjects[homepage_num] != before_subjects[homepage_num]:
                for subject, url in cur_subjects[homepage_num]:
                    if (subject, url) not in before_subjects[homepage_num]:
                        different_subject_cnt += 1

            if attempt != 1 and cur_subjects[homepage_num] != before_subjects[homepage_num] and different_subject_cnt < 7:
                for subject, url in cur_subjects[homepage_num]:
                    if (subject, url) not in before_subjects[homepage_num]:
                        print(f"새로운 공지 제목 : {subject}")
                        print(f"새로운 공지 URL : {url.strip()}")
                        await channel.send(f'새로운 공지 제목 : {subject} \n {url.strip()}')

            before_subjects[homepage_num] = copy.deepcopy(cur_subjects[homepage_num])
            cur_subjects[homepage_num].clear()

            homepage_num += 1
            if homepage_num == 12:
                homepage_num -= 12

            await asyncio.sleep(random.uniform(5.0, 10.0))

    attempt += 1

bot.run(config['discord_token'])