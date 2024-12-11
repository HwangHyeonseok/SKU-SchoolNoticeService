# sungkyul univ crawling (20240329)
# - 기본 디스코드 공지사항 크롤링 봇
# --------------------------- 보고된 문제 ---------------------------------------
# [오류 내용]
# discord.errors.ConnectionClosed: Shard ID None WebSocket closed with 1000
# [해결]
# while True: 구문 대신 discord.ext.tasks 에서 제공하는 @tasks.loop 사용
# ------------------------------------------------------------------------------

# 1. driver 만들기
# User Agent Data 변경하기 (mobile 기준)

# change_UA_data.py 사용 시 적용되는 창 전환 : https://wikidocs.net/82611

# CDP Command 레퍼런스 사이트 모음
# CMD 모두 수록 / 파랑 사이트 : https://chromedevtools.github.io/devtools-protocol/tot/Emulation/
# 셀레니움 언어별 /초록 사이트 : https://www.selenium.dev/documentation/webdriver/actions_api/

import chromedriver_autoinstaller
import random, time
from user_agents import parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

import copy

from discord.ext import commands
import discord
import asyncio

import json

# config.json 파일 로드
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()


bot = commands.Bot(command_prefix='!',intents=discord.Intents.all()) # 명령을 할 때 '!'을 넣어서 명령어를 실행

@bot.event
async def on_ready(): # 봇이 시작될 때 한 번 실행되는 함수
    print(f'Login bot: {bot.user}')

@bot.command()
async def 공지사항(message): # "!공지사항"를 대화창에 입력한 경우 실행되는 함수
    await message.channel.send('성결대학교 공지사항을 모니터링합니다.') # 봇이 메세지가 온 채널에 "성결대학교 공지사항을 모니터링합니다." 라는 메시지를 보내준다.
        #  ========================================== 변수 ===================================================
    # local_computer_user_agent_txt_path : user-agent 15000개 데이터 txt파일이 저장된 공간 (local)
    # GCP_server_computer_user_agent_txt_path : user-agent 15000개 데이터 txt파일이 저장된 공간 (GCP 경로)
    
    before_subjects = [[] for _ in range(14)] # 14개의 2차원 빈 배열 초기화 [홈페이지 번째수][(게시글 제목, 게시글 url)]
    cur_subjects = [[] for _ in range(14)] # 14개의 2차원 빈 배열 초기화 [홈페이지 번째수][(게시글 제목, 게시글 url)]
    homepage_num = 0 # 학교 홈페이지 URL index
    attempt = 1 # 공지사항 순회 횟수
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
    # ====================================================================================================
    # 드라이버 자동 최신 버전 업데이트
    chromedriver_autoinstaller.install()
    # user agent data를 바꾸는 함수
    def make_user_agent(ua,is_mobile): 
        user_agent = parse(ua)
        model = user_agent.device.model
        platform = user_agent.os.family
        platform_version = user_agent.os.version_string + ".0.0"
        version = user_agent.browser.version[0]
        ua_full_version = user_agent.browser.version_string
        architecture = "x86"
        print(platform)
        if is_mobile:
            platform_info = "Linux armv8l"
            architecture= ""
        else: # Window 기준
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
                "mobile":is_mobile #True, False
            }
        }
        return RET_USER_AGENT
    # 랜덤한 user-agent가 담긴 useragents.txt 파일을 읽어온다.
    def read_agents():
        agents = []
        f = open(config['GCP_server_computer_user_agent_txt_path'],"r",encoding="utf8")
        while True:
            line = f.readline()
            if not line:
                break
            agents.append(line.rstrip())
        return agents
    # driver을 만들어주는 함수
        # 쿠키 저장장소 : C:\cookies\{cookie_account_id}
        # cookie_account_id : 쿠키 파일로 생성될 폴더 이름
    def make_driver():
        try:
            # 해상도 설정
            pc_device = ["1920,1440","1920,1200","1920,1080","1600,1200","1600,900",
                            "1536,864", "1440,1080","1440,900","1360,768"
                    ]

            mo_device = [
                        "360,640", "360,740", "375,667", "375,812", "412,732", "412,846",
                        "412,869", "412,892", "412,915"
                    ]

            width,height = random.choice(mo_device).split(",")
            
            UA_list = read_agents()
            #UA = "Mozilla/5.0 (Linux; Android 9; Mi A2 Lite Build/PKQ1.180917.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.132 Mobile Safari/537.36" # user agent 조작
            UA = random.choice(UA_list)  #seed = time.time()
            
            options = uc.ChromeOptions()
            
            # User Agent 속이기
            options.add_argument(f'--user-agent={UA}') # User Agent 변경
            options.add_argument(f"--window-size={width},{height}")
            options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
            options.add_argument('--disable-logging')
            options.add_argument('--disable-popup-blocking') # uc에서 새 탭 열기 허용

            driver = uc.Chrome(options=options, version_main=122) # 일시적인 버전 오류가 있는 경우 version_main=120~122

            UA_Data = make_user_agent(UA, True) # user agent data를 바꾸는 함수 호출 

            driver.execute_cdp_cmd("Network.setUserAgentOverride", UA_Data) # user agent data를 바꾸기 위해 필요한 코드 

            # Max Touch Point 변경
            # 모바일은 보통 1,5 / PC는 보통 0,2
            Mobile = {"enabled":True, "maxTouchPoints" : random.choice([1,5])}
            driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", Mobile)
            driver.execute_cdp_cmd("Emulation.setNavigatorOverrides",{"platform":"Linux armv8l"})
            # DeviceMetrics 변경(Emulation 쪽에서 setDeviceMetricsOverride 적용)
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width":int(width),
                "height":int(height),
                "deviceScaleFactor":1,
                "mobile":True,
            })

            # 위치 정보 변경 (Geo Location 변경) 
            # 서울쪽에 원하는 위치를 잡기 위해서는 구글에 "위도 경도 지도" 검색 후 좌상단, 우하단 위도/경도값을 가져오면 된다.
            # 찾는 사이트 : http://map.esran.com/
            def generate_random_geolcation():
                ltop_lat = 37.61725745260699 # 좌 위도
                ltop_long = 126.92437164480178 # 좌 경도
                rbottom_lat = 37.56825361755575 # 우 위도
                rbottom_long = 127.05771697149082 # 우 경도

                targetLat = random.uniform(rbottom_lat, ltop_lat)
                targetLong = random.uniform(ltop_long, rbottom_long)
                return {"latitude" : targetLat, "longitude" : targetLong, "accuracy":100}
            GEO_DATA = generate_random_geolcation()
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", GEO_DATA)

            # User Agent 적용
            driver.execute_cdp_cmd("Emulation.setUserAgentOverride",UA_Data)
            print(width,height)
            driver.set_window_size(int(width),int(height))

            return driver
        
        except Exception as e:
            print(e)
            driver = None
            return driver

    driver = make_driver()

    while True:
        print(f"{attempt} 번째 시도중입니다.")

        for sku_site_link in sku_site_links: # [홈페이지 단위 - ex. 새소식, 학사 ...]
            try:
                driver.get(sku_site_link) # 창 띄우기
            except:
                print(f"[ERROR 001] 성결대학교 홈페이지 오류입니다. {sku_site_link} 페이지를 띄우지 못했습니다.")
                await message.channel.send(f"[ERROR 001] 성결대학교 홈페이지 오류입니다. {sku_site_link} 페이지를 띄우지 못했습니다.") # 봇이 메세지가 온 채널에 메시지 보내기
            driver.implicitly_wait(30)

            # 상위 10개 공지를 리스트에 저장
            try:
                post_elements = driver.find_elements(By.CSS_SELECTOR, '.td-subject > a')
            except:
                print("[ERROR 002] 성결대학교 상위 10개 공지 전체 element CSS_SELECTOR 오류입니다.")
                await message.channel.send("[ERROR 002] 성결대학교 상위 10개 공지 전체 element CSS_SELECTOR 오류입니다.") # 봇이 메세지가 온 채널에 메시지 보내기

            try:
                for post_element in post_elements: # 공지들 순회하면서 게시물의 URL, 제목 저장
                    url = post_element.get_attribute('href')
                    subject_element = post_element.find_element(By.CSS_SELECTOR, 'strong') # 게시물 제목
                    subject = subject_element.text
                    cur_subjects[homepage_num].append((subject, url))
            except:
                print("[ERROR 003] 성결대학교 게시물의 제목이나 URL을 받아오지 못했습니다.")
                await message.channel.send("[ERROR 003] 성결대학교 게시물의 제목이나 URL을 받아오지 못했습니다.") # 봇이 메세지가 온 채널에 메시지 보내기

            # 첫 번째 순회일 때는 before_subjects 리스트에 초기값 세팅해야 하므로 이전 공지와 비교 X (두 번째 공지부터 비교)
            # 이전 공지와 바뀐 것이 있는 경우 (새로운 공지가 올라온 경우)
            if attempt != 1 and cur_subjects[homepage_num] != before_subjects[homepage_num]: 
                # 이전 공지와 바뀐 것이 있는 경우 : 1) 바뀐 공지를 찾아서 2) 바뀐 공지의 공지 제목과 URL을 카카오톡 메시지로 보내고 3) 이전 공지를 현재 공지로 최신화 해준다.
                # 1) 바뀐 공지 찾기
                for subject,url in cur_subjects[homepage_num]:
                    if (subject, url) not in before_subjects[homepage_num]: # 이전 공지와 비교했을 때 없는 것이 있다면 바뀐 공지이다.
                        print(f"새로운 공지 제목 : {subject}")
                        print(f"새로운 공지 URL : {url.strip()}")  
                        # 2) 바뀐 공지의 공지 제목과 URL을 디스코드 메시지로 보낸다.
                        await message.channel.send(f'새로운 공지 제목 : {subject} \n {url.strip()}') # 봇이 메세지가 온 채널에 메시지 보내기          

            # 3) 이전 공지를 현재 공지로 최신화 해준다.
            #before_subjects[i] = cur_subjects[i] # 완벽한 얕은 복사 (운명공동체)
            #before_subjects[i] = cur_subjects[i].copy() # 리스트 안의 리스트만 얕은 복사 ('리스트 안의 리스트'만 운명공동체)
            before_subjects[homepage_num] = copy.deepcopy(cur_subjects[homepage_num]) # 깊은 복사 (나는 나 너는 너)
            cur_subjects[homepage_num].clear()

            # 다음 홈페이지 index로
            homepage_num += 1
            if(homepage_num == 14):
                homepage_num -= 14
                
            #time.sleep(random.uniform(10.0, 30.0)) # 한 페이지를 비교 완료하고 10초~30초 대기 (홈페이지 부하 방지)
            await asyncio.sleep(random.uniform(20.0, 30.0))

        attempt += 1 # 전체 공지사항 순회 횟수 추가
        #time.sleep(random.uniform(900.0, 960.0)) # 전체 페이지를 한 번 돌고나서 15분 ~ 16분 대기 (홈페이지 부하 방지)    
        await asyncio.sleep(random.uniform(20.0, 30.0))

bot.run(config['bot_id'])