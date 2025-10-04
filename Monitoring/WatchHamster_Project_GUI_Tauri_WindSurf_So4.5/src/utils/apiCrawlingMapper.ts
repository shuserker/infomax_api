// InfoMax API 크롤링 기반 매핑 시스템
// 실제 API 문서에서 크롤링된 정보와 매핑

interface CrawledApiInfo {
  url: string
  title: string
  parameters: CrawledParameter[]
  pythonCode: string
  outputFields: CrawledOutputField[]
  isCrawled: boolean // 크롤링 성공 여부
}

interface CrawledParameter {
  name: string
  type: string
  required: boolean
  description: string
  example?: string
}

interface CrawledOutputField {
  name: string
  type: string
  description: string
}

// 크롤링된 API 정보 매핑표
export const crawledApiMapping: Record<string, CrawledApiInfo> = {
  // 채권 발행정보 (크롤링 완료)
  'bond/basic_info': {
    url: '/api/bond/basic_info',
    title: '발행정보',
    isCrawled: true,
    parameters: [
      { name: 'stdcd', type: 'String', required: false, description: '표준코드', example: 'KR6000661159' },
      { name: 'inttype_1', type: 'String', required: false, description: '이자지급방법 [11:할인채, 12:복리채, 13:이표채, 14:단리채, 15:복5단2, 21:FRN]' },
      { name: 'issuedate', type: 'String', required: false, description: '발행일' },
      { name: 'expidate', type: 'String', required: false, description: '만기일' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/bond/basic_info'

params = {"stdcd":"KR6000661159","inttype_1":"","issuedate":"","expidate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'stdcd', type: 'String', description: '표준코드' },
      { name: 'shortcd', type: 'String', description: '단축코드' },
      { name: 'bondnm', type: 'String', description: '한글종목명' },
      { name: 'engnm', type: 'String', description: '영문종목명' },
      { name: 'compnm', type: 'String', description: '회사명' },
      { name: 'issuedate', type: 'String', description: '발행일' },
      { name: 'presaledate', type: 'String', description: '선매출일' },
      { name: 'expidate', type: 'String', description: '만기일' },
      { name: 'issuerate', type: 'Number', description: '발행률' },
      { name: 'repayrate', type: 'Number', description: '상환이율' },
      { name: 'couponrate', type: 'Number', description: '표면이율' },
      { name: 'issueamt', type: 'Number', description: '발행액' },
      { name: 'intpayterm', type: 'String', description: '이자지급기간' },
      { name: 'lstgb', type: 'String', description: '상장구분' },
      { name: 'lstdate', type: 'String', description: '상장일' },
      { name: 'lstclosedate', type: 'String', description: '상장폐지일' },
      { name: 'lstamt', type: 'Number', description: '상장잔액' },
      { name: 'gurttype', type: 'String', description: '보증형태' },
      { name: 'optionkind', type: 'String', description: '옵션종류' },
      { name: 'substprice', type: 'Number', description: '대용가' },
      { name: 'currencygb', type: 'String', description: '통화구분' },
      { name: 'collectgb', type: 'String', description: '공모사모구분' },
      { name: 'subordbond', type: 'String', description: '후순위채구분' },
      { name: 'ksccd', type: 'String', description: '증권전산 회사코드' },
      { name: 'absgb', type: 'String', description: 'ABS(자산유동화)구분' },
      { name: 'bhgigwancd', type: 'String', description: '발행기관코드' },
      { name: 'inttype_1', type: 'String', description: '이자지급방법' },
      { name: 'crdtparcomp1', type: 'String', description: '신용평가기관1' },
      { name: 'crdtparcomp2', type: 'String', description: '신용평가기관2' },
      { name: 'crdtparcomp3', type: 'String', description: '신용평가기관3' },
      { name: 'crdtparcomp4', type: 'String', description: '신용평가기관4' },
      { name: 'crdtparrate1', type: 'String', description: '신용평가등급1' },
      { name: 'crdtparrate2', type: 'String', description: '신용평가등급2' },
      { name: 'crdtparrate3', type: 'String', description: '신용평가등급3' },
      { name: 'crdtparrate4', type: 'String', description: '신용평가등급4' },
      { name: 'hybridgb', type: 'String', description: '신종자본증권 여부' },
      { name: 'aclass', type: 'String', description: '인포맥스 채권 대분류' },
      { name: 'bclass', type: 'String', description: '인포맥스 채권 중분류' },
      { name: 'cclass', type: 'String', description: '인포맥스 채권 소분류' },
      { name: 'wonissueamt', type: 'Number', description: '원화표시 발행액' },
      { name: 'wonlstamt', type: 'Number', description: '원화표시 상장잔액' },
      { name: 'estyld', type: 'Number', description: '민평 3사 수익률' },
      { name: 'estdanga', type: 'Number', description: '민평 3사 가격' },
      { name: 'duration', type: 'Number', description: '듀레이션' },
      { name: 'exbalcond', type: 'String', description: '특이발행조건' },
      { name: 'condcapcertgb', type: 'String', description: '조건부자본증권유형' }
      // 인수기관 리스트 필드들 (agentorg_list_01~10, rcvorg_list_01~18)도 있지만 간략화
    ]
  },

  // 채권 체결정보 (이전 크롤링 정보 기반)
  'bond/market/mn_hist': {
    url: '/api/bond/market/mn_hist',
    title: '체결정보',
    isCrawled: true,
    parameters: [
      { name: 'stdcd', type: 'String', required: false, description: '표준코드' },
      { name: 'market', type: 'String', required: false, description: '시장구분', example: '장외' },
      { name: 'startDate', type: 'String', required: false, description: '시작일자', example: '20250401' },
      { name: 'endDate', type: 'String', required: false, description: '종료일자', example: '20250401' },
      { name: 'aclassnm', type: 'String', required: false, description: '대분류' },
      { name: 'volume', type: 'String', required: false, description: '거래량' },
      { name: 'allcrdtrate', type: 'String', required: false, description: '신용등급' },
      { name: 'yld', type: 'String', required: false, description: '거래수익률' },
      { name: 'estyld', type: 'String', required: false, description: '민평수익률' }
    ],
    pythonCode: `import ssl, json, requests
ssl._create_default_https_context = ssl._create_unverified_context
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/bond/market/mn_hist'

params = {"stdcd":"","market":"장외","startDate":"20250401","endDate":"20250401","aclassnm":"","volume":"","allcrdtrate":"","yld":"","estyld":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'stdcd', type: 'String', description: '표준코드' },
      { name: 'bondnm', type: 'String', description: '채권명' },
      { name: 'tradedate', type: 'String', description: '거래일자' },
      { name: 'closeprice', type: 'Number', description: '종가' },
      { name: 'volume', type: 'Number', description: '거래량' },
      { name: 'amount', type: 'Number', description: '거래대금' },
      { name: 'yld', type: 'Number', description: '거래수익률' },
      { name: 'estyld', type: 'Number', description: '민평수익률' }
    ]
  },

  // 채권 시가평가 (이전 크롤링 정보 기반)
  'bond/marketvaluation': {
    url: '/api/bond/marketvaluation',
    title: '종목별 시가평가',
    isCrawled: true,
    parameters: [
      { name: 'stdcd', type: 'String', required: true, description: '표준코드', example: 'KR101501DA32' },
      { name: 'bonddate', type: 'String', required: false, description: '기준일자' }
    ],
    pythonCode: `import ssl, json, requests
ssl._create_default_https_context = ssl._create_unverified_context
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/bond/marketvaluation'

params = {"stdcd":"KR101501DA32","bonddate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'stdcd', type: 'String', description: '표준코드' },
      { name: 'bondnm', type: 'String', description: '채권명' },
      { name: 'bonddate', type: 'String', description: '기준일자' },
      { name: 'price', type: 'Number', description: '시가평가 가격' },
      { name: 'yield', type: 'Number', description: '시가평가 수익률' }
    ]
  },

  // 주식 일별 (이전 크롤링 정보 기반)
  'stock/hist': {
    url: '/api/stock/hist',
    title: '일별',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '종목코드', example: '005930' },
      { name: 'startDate', type: 'Number', required: false, description: '시작일자' },
      { name: 'endDate', type: 'Number', required: false, description: '종료일자' }
    ],
    pythonCode: `import ssl, json, requests
ssl._create_default_https_context = ssl._create_unverified_context
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/hist'

params = {"code":"005930","startDate":"","endDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'name', type: 'String', description: '종목명' },
      { name: 'date', type: 'String', description: '일자' },
      { name: 'open', type: 'Number', description: '시가' },
      { name: 'high', type: 'Number', description: '고가' },
      { name: 'low', type: 'Number', description: '저가' },
      { name: 'close', type: 'Number', description: '종가' },
      { name: 'volume', type: 'Number', description: '거래량' }
    ]
  },

  // 주식 코드 검색 (이전 크롤링 정보 기반)
  'stock/code': {
    url: '/api/stock/code',
    title: '코드 검색/리스트',
    isCrawled: true,
    parameters: [
      { name: 'search', type: 'String', required: false, description: '통합검색' },
      { name: 'code', type: 'String', required: false, description: '종목코드' },
      { name: 'name', type: 'String', required: false, description: '종목명' },
      { name: 'isin', type: 'String', required: false, description: 'ISIN코드' },
      { name: 'market', type: 'String', required: false, description: '시장구분' },
      { name: 'type', type: 'String', required: false, description: '종목구분', example: 'ST' }
    ],
    pythonCode: `import ssl, json, requests
ssl._create_default_https_context = ssl._create_unverified_context
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/code'

params = {"search":"","code":"","name":"","isin":"","market":"","type":"ST"}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'name', type: 'String', description: '종목명' },
      { name: 'isin', type: 'String', description: 'ISIN코드' },
      { name: 'market', type: 'String', description: '시장구분' },
      { name: 'type', type: 'String', description: '종목구분' }
    ]
  },

  // 외환 고시환율-일별 (새로 크롤링됨)
  'fx/exchangerate/hist': {
    url: '/api/fx/exchangerate/hist',
    title: '고시환율-일별',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '3자리 통화코드', example: 'USD' },
      { name: 'enddate', type: 'String', required: false, description: '조회 종료일 (YYYYMMDD) 미입력시 today' },
      { name: 'startdate', type: 'String', required: false, description: '조회 시작일 (YYYYMMDD) 미입력시 endDate-30' },
      { name: 'quote', type: 'String', required: false, description: '특정회차 (0000) 미입력시 최종회차' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/fx/exchangerate/hist'

params = {"code":"USD","enddate":"","startdate":"","quote":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'String', description: '일자' },
      { name: 'quote_num', type: 'String', description: '회차' },
      { name: 'code', type: 'String', description: '통화코드' },
      { name: 'krw_rate', type: 'Number', description: '고시환율' },
      { name: 'wire_sending', type: 'Number', description: '송금 보낼 때 (BID)' },
      { name: 'wire_receiving', type: 'Number', description: '송금 받을 때 (ASK)' },
      { name: 'cash_bid', type: 'Number', description: '현찰 살 때 (BID)' },
      { name: 'cash_ask', type: 'Number', description: '현찰 팔 때 (ASK)' },
      { name: 'usd_rate', type: 'Number', description: '달러환산율' }
    ]
  },

  // ETF 일별 NAV (새로 크롤링됨)
  'etf/hist': {
    url: '/api/etf/hist',
    title: '일별 NAV',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드 or ISIN 코드', example: '069500' },
      { name: 'endDate', type: 'Number', required: false, description: '조회 종료일 (YYYYMMDD) 미입력시 today' },
      { name: 'startDate', type: 'Number', required: false, description: '조회 시작일 (YYYYMMDD) 미입력시 endDate-30' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/etf/hist'

params = {"code":"069500","endDate":"","startDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'nav', type: 'Number', description: 'NAV' },
      { name: 'tracking_error_rate', type: 'Number', description: '추적오차율' },
      { name: 'disparate_ratio', type: 'Number', description: '괴리율' },
      { name: 'net_asset', type: 'Number', description: '순자산총액' }
    ]
  },

  // 지수 코드 검색/리스트 (새로 크롤링됨)
  'index/code': {
    url: '/api/index/code',
    title: '코드 검색/리스트',
    isCrawled: true,
    parameters: [
      { name: 'type', type: 'String', required: false, description: '지수 종류 구분 (K:코스피, Q:코스닥, X:KRX, F:선물, O:옵션, G:Global&other, T:일반상품&etc, M:멀티에셋, N:코넥스)' },
      { name: 'kr_name', type: 'String', required: false, description: '지수명 한글 검색' },
      { name: 'en_name', type: 'String', required: false, description: '지수명 영문 검색' },
      { name: 'code', type: 'String', required: false, description: '지수코드 검색' },
      { name: 'return', type: 'String', required: false, description: 'Return 타입 구분 (PR:Price Return, TR:Total Return, NTR:Net Total Return)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/index/code'

params = {"type":"","kr_name":"","en_name":"","code":"","return":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '지수 코드' },
      { name: 'index_type', type: 'String', description: '자산/시장 구분' },
      { name: 'strat_type', type: 'String', description: '전략 구분' },
      { name: 'return_type', type: 'String', description: 'Return 타입 구분' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'en_name', type: 'String', description: '영문 종목약명' }
    ]
  },

  // 선물 코드 검색/리스트 (새로 크롤링됨)
  'future/code': {
    url: '/api/future/code',
    title: '코드 검색/리스트',
    isCrawled: true,
    parameters: [
      { name: 'kr_name', type: 'String', required: false, description: '종목명 한글 검색' },
      { name: 'underlying_type', type: 'String', required: false, description: '기초자산 종류 (F:지수, C:금리/FX/일반, G:글로벌, L:개별주식)' },
      { name: 'underlying_code', type: 'String', required: false, description: '기초자산 코드 (01:코스피200, 65:3년국채, 67:10년국채, 75:미국달러 등)' },
      { name: 'spread', type: 'String', required: false, description: '스프레드 상품만 조회 (Y) 선물 상품만 조회 (N) 미입력시 선물만 출력' },
      { name: 'isin', type: 'String', required: false, description: 'ISIN 코드 검색' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/code'

params = {"kr_name":"","underlying_type":"","underlying_code":"","spread":"","isin":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '상품 종목코드' },
      { name: 'underlying_type', type: 'String', description: '기초자산 종류' },
      { name: 'underlying_type_code', type: 'String', description: '자산종류 코드' },
      { name: 'underlying', type: 'String', description: '기초자산' },
      { name: 'underlying_code', type: 'String', description: '기초자산 코드' },
      { name: 'underlying_isin', type: 'String', description: '기초자산 표준코드' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'en_name', type: 'String', description: '영문 종목명' },
      { name: 'maturity_YYMM', type: 'String', description: '만기년월 (YYMM)' },
      { name: 'listed_date', type: 'Number', description: '상장 일자' },
      { name: 'unlisting_date', type: 'Number', description: '상장 폐지일' },
      { name: 'last_trading_date', type: 'Number', description: '최종 거래일' },
      { name: 'last_settle_date', type: 'Number', description: '최종 결제일' },
      { name: 'contract_unit', type: 'Number', description: '거래 단위' },
      { name: 'multiplier', type: 'Number', description: '거래 승수' },
      { name: 'close_price', type: 'Number', description: '현재가' },
      { name: 'settle_type', type: 'String', description: '최종 결제 방법' },
      { name: 'is_spread', type: 'String', description: '스프레드 구분 (Y, N)' },
      { name: 'spread_near_isin', type: 'String', description: '스프레드 근월물 표준코드' },
      { name: 'spread_far_isin', type: 'String', description: '스프레드 원월물 표준코드' },
      { name: 'spread_type', type: 'String', description: '스프레드 분류' }
    ]
  },

  // 옵션 코드 검색/리스트 (새로 크롤링됨)
  'option/code': {
    url: '/api/option/code',
    title: '코드 검색/리스트',
    isCrawled: true,
    parameters: [
      { name: 'kr_name', type: 'String', required: false, description: '종목명 한글 검색' },
      { name: 'underlying_code', type: 'String', required: false, description: '기초자산 코드 [01:코스피200, 05:미니코스피, 06:코스닥150, 09:코스피위클리(목), AF:코스피위클리(월)]', example: '01' },
      { name: 'maturity', type: 'String', required: false, description: '만기년월 (YYYYMM)' },
      { name: 'option', type: 'String', required: false, description: '옵션종류 (C: Call / P: Put)' },
      { name: 'atm', type: 'String', required: false, description: 'ATM구분 (Y:ATM, N:ATM제외, I:ITM, O:OTM, ALL:전체) 미입력시 ATM' },
      { name: 'isin', type: 'String', required: false, description: 'ISIN 검색' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/option/code'

params = {"kr_name":"","underlying_code":"01","maturity":"","option":"","atm":"","isin":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '영업일자' },
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '옵션 종목코드' },
      { name: 'underlying', type: 'String', description: '기초자산' },
      { name: 'option_type', type: 'String', description: '옵션 종류' },
      { name: 'strike_price', type: 'Number', description: '행사가' },
      { name: 'isATM', type: 'String', description: 'ATM구분 (ATM / ITM / OTM)' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'en_name', type: 'String', description: '영문 종목명' },
      { name: 'maturity_YYYYMM', type: 'String', description: '만기년월 (YYYYMM)' },
      { name: 'listed_date', type: 'Number', description: '상장일자' },
      { name: 'unlisting_date', type: 'Number', description: '상장 폐지일' },
      { name: 'last_trading_date', type: 'Number', description: '최종 거래일' },
      { name: 'contract_unit', type: 'Number', description: '거래 단위' },
      { name: 'multiplier', type: 'Number', description: '거래 승수' },
      { name: 'close_price', type: 'Number', description: '현재가' }
    ]
  },

  // 주식 기본 정보 (새로 크롤링됨)
  'stock/info': {
    url: '/api/stock/info',
    title: '기본',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드 or ISIN 코드 (복수 코드 조회시 ,로 구분)', example: '259960' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD) 미입력시 today-1', example: '20250211' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/info'

params = {"code":"259960","date":"20250211"}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'market', type: 'String', description: '시장 구분' },
      { name: 'equity_type', type: 'String', description: '증권 구분' },
      { name: 'base_price', type: 'Number', description: '기준가' },
      { name: 'open_price', type: 'Number', description: '시가' },
      { name: 'high_price', type: 'Number', description: '고가' },
      { name: 'low_price', type: 'Number', description: '저가' },
      { name: 'close_price', type: 'Number', description: '현재가(종가)' },
      { name: 'change', type: 'Number', description: '전일대비' },
      { name: 'change_rate', type: 'Number', description: '등락률' },
      { name: 'trading_volume', type: 'Number', description: '거래량' },
      { name: 'trading_value', type: 'Number', description: '거래대금' },
      { name: 'listed_shares', type: 'Number', description: '상장주식수' }
    ]
  },

  // ETF i-NAV (일중) (새로 크롤링됨)
  'etf/intra': {
    url: '/api/etf/intra',
    title: 'i-NAV (일중)',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드 or ISIN 코드', example: '069500' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD) 미입력시 today [제한: 최근 1개월]' },
      { name: 'endTime', type: 'Number', required: false, description: '조회 종료시간 미만 (HHMMSS) 미입력시 조회시작시간~전체' },
      { name: 'startTime', type: 'Number', required: false, description: '조회 시작시간 이상 (HHMMSS) 미입력시 전체~조회종료시간' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/etf/intra'

params = {"code":"069500","date":"","endTime":"","startTime":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'time', type: 'Number', description: '시간' },
      { name: 'close_price', type: 'Number', description: '현재가' },
      { name: 'trading_volume', type: 'Number', description: '거래량' },
      { name: 'trading_value', type: 'Number', description: '거래대금' },
      { name: 'i-nav', type: 'Number', description: 'NAV(IIV)' },
      { name: 'tracking_error_rate', type: 'Number', description: '추적오차율' },
      { name: 'disparate_ratio', type: 'Number', description: '괴리율' }
    ]
  },

  // 선물 일별 (새로 크롤링됨)
  'future/hist': {
    url: '/api/future/hist',
    title: '일별',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '상품 종목코드 8자리', example: '101V6000' },
      { name: 'endDate', type: 'Number', required: false, description: '조회 종료일 (YYYYMMDD) 미입력시 today', example: '20240321' },
      { name: 'startDate', type: 'Number', required: false, description: '조회 시작일 (YYYYMMDD) 미입력시 endDate-30' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/hist'

params = {"code":"101V6000","endDate":"20240321","startDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '상품 종목코드' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'base_price', type: 'Number', description: '기준가' },
      { name: 'open_price', type: 'Number', description: '시가' },
      { name: 'high_price', type: 'Number', description: '고가' },
      { name: 'low_price', type: 'Number', description: '저가' },
      { name: 'close_price', type: 'Number', description: '현재가' },
      { name: 'change', type: 'Number', description: '전일대비' },
      { name: 'change_rate', type: 'Number', description: '등락률' },
      { name: 'openInterest_volume', type: 'Number', description: '미결제약정 수량' },
      { name: 'trading_volume', type: 'Number', description: '거래량' },
      { name: 'trading_value', type: 'Number', description: '거래대금 (천원)' },
      { name: 'blocktrade_volume', type: 'Number', description: '협의 대량거래 약정수량' },
      { name: 'blocktrade_value', type: 'Number', description: '협의 대량거래 약정대금 (천원)' },
      { name: 'settle_price', type: 'Number', description: '정산가' },
      { name: 'ktb_open_ytm', type: 'Number', description: '국채선물 시가 수익률' },
      { name: 'ktb_high_ytm', type: 'Number', description: '국채선물 고가 수익률' },
      { name: 'ktb_low_ytm', type: 'Number', description: '국채선물 저가 수익률' },
      { name: 'ktb_close_ytm', type: 'Number', description: '국채선물 종가 수익률' },
      { name: 'underlying_type', type: 'String', description: '기초자산 종류' },
      { name: 'underlying_type_code', type: 'String', description: '자산종류 코드' },
      { name: 'underlying', type: 'String', description: '기초자산' },
      { name: 'underlying_code', type: 'String', description: '기초자산 코드' },
      { name: 'underlying_isin', type: 'String', description: '기초자산 표준코드' },
      { name: 'underlying_price', type: 'Number', description: '기초자산 가격' },
      { name: 'theoretical_price', type: 'Number', description: '이론가' },
      { name: 'underlying_basis', type: 'Number', description: '시장 베이시스' },
      { name: 'theoretical_basis', type: 'Number', description: '이론 베이시스' },
      { name: 'ktb_ksda_price', type: 'Number', description: '증권협회 현물가' },
      { name: 'ktb_basket_ytm', type: 'Number', description: '국채선물 바스켓 수익률' }
    ]
  },

  // 뉴스 검색 (새로 크롤링됨)
  'news/search': {
    url: '/api/news/search',
    title: '연합인포맥스 뉴스',
    isCrawled: true,
    parameters: [
      { name: 'news_id', type: 'String', required: false, description: '뉴스ID' },
      { name: 'title', type: 'String', required: false, description: '제목' },
      { name: 'summary', type: 'String', required: false, description: '요약' },
      { name: 'urgency', type: 'String', required: false, description: '긴급뉴스 구분 ("Y" 또는 "true" 입력)' },
      { name: 'date', type: 'String', required: false, description: '일자' },
      { name: 'startDate', type: 'String', required: false, description: '조회 시작일 (YYYYMMDD) 미입력시 endDate-30', example: '20250224' },
      { name: 'endDate', type: 'String', required: false, description: '조회 종료일 (YYYYMMDD) 미입력시 today', example: '20250224' },
      { name: 'time', type: 'String', required: false, description: '시간', example: '230126' },
      { name: 'source', type: 'String', required: false, description: '출처' },
      { name: 'writer', type: 'String', required: false, description: '기자' },
      { name: 'category', type: 'String', required: false, description: '카테고리 미입력시 전체 검색 (경제, 정치, 사회, 인사, 문화, 스포츠, 전국, 세계)' },
      { name: 'keywords', type: 'String', required: false, description: '관련 종목' },
      { name: 'body', type: 'String', required: false, description: '본문' },
      { name: 'search', type: 'String', required: false, description: '검색어' },
      { name: 'code', type: 'String', required: false, description: '종목 관련 뉴스 조회 (국내 주식코드 6자리)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/news/search'

params = {"news_id":"","title":"","summary":"","urgency":"","date":"","startDate":"20250224","endDate":"20250224","time":"230126","source":"","writer":"","category":"","keywords":"","body":"","search":"","code":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'news_id', type: 'Number', description: '뉴스ID' },
      { name: 'title', type: 'Number', description: '제목' },
      { name: 'summary', type: 'Number', description: '요약' },
      { name: 'urgency', type: 'Number', description: '긴급뉴스 구분' },
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'time', type: 'Number', description: '시간' },
      { name: 'source', type: 'Number', description: '출처' },
      { name: 'writer', type: 'Number', description: '기자 (\',\'로 구분)' },
      { name: 'category', type: 'Number', description: '카테고리 (\',\'로 구분)' },
      { name: 'keywords', type: 'Number', description: '관련 종목 (\',\'로 구분)' },
      { name: 'body', type: 'Number', description: '본문' }
    ]
  },

  // 기업정보 상장기업 검색 (새로 크롤링됨)
  'company/listed': {
    url: '/api/company/listed',
    title: '상장기업 검색',
    isCrawled: true,
    parameters: [
      { name: 'name', type: 'String', required: false, description: '한글 기업명 검색', example: '넥스콘' },
      { name: 'code', type: 'Number', required: false, description: '상장기업 종목코드 6자리' },
      { name: 'industry', type: 'String', required: false, description: '재무 업종분류 (복수 분류 조회시 ,로 구분) 제조업/은행업/보험업/증권업/투자금융업/신용금고업/종합금융업/여신금융업/기타금융업' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/company/listed'

params = {"name":"넥스콘","code":"","industry":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '상장 종목코드 6자리' },
      { name: 'industry', type: 'String', description: '재무 업종분류' },
      { name: 'groupname', type: 'String', description: '그룹사' },
      { name: 'kr_name', type: 'String', description: '한글 기업명' },
      { name: 'en_name', type: 'String', description: '영문 기업명' },
      { name: 'establish_date', type: 'String', description: '설립일자' },
      { name: 'president', type: 'String', description: '대표자' },
      { name: 'audit', type: 'String', description: '회계감사인' },
      { name: 'taxpayer_number', type: 'String', description: '사업자등록번호' },
      { name: 'registration_number', type: 'String', description: '법인등록번호' }
    ]
  },

  // 채권 시가평가 (평가사별) (새로 크롤링됨)
  'bond/marketvalue': {
    url: '/api/bond/marketvalue',
    title: '종목별 시가평가_평가사별',
    isCrawled: true,
    parameters: [
      { name: 'stdcd', type: 'String', required: true, description: '표준코드', example: 'KR101501DA32' },
      { name: 'estcompgb', type: 'String', required: false, description: '시가평가사구분코드 [KBP:한국자산평가, NIC:나이스피앤아이, KIS:키스자산평가, FNP:에프앤자산평가]' },
      { name: 'bonddate', type: 'String', required: false, description: '일자', example: '20250219' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/bond/marketvalue'

params = {"stdcd":"KR101501DA32","estcompgb":"","bonddate":"20250219"}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'estcompgb', type: 'String', description: '시가평가사 구분' },
      { name: 'stdcd', type: 'String', description: '종목코드' },
      { name: 'bonddate', type: 'String', description: '적용일자' },
      { name: 'estyld', type: 'Number', description: '평가수익률' },
      { name: 'estdanga', type: 'Number', description: '평가액 익일 (T+1)' },
      { name: 'estdangat0', type: 'Number', description: '평가액 당일 (T+0)' },
      { name: 'duration', type: 'Number', description: '듀레이션' },
      { name: 'convexity', type: 'Number', description: '컨벡시티' }
    ]
  },

  // ETF 포트폴리오 구성내역 (새로 크롤링됨)
  'etf/port': {
    url: '/api/etf/port',
    title: 'PDF',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '069500' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD) 미입력시 today' },
      { name: 'sort', type: 'String', required: false, description: '정렬 기준 (평가금액:value / 수량:volume) 미입력시 평가금액' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/etf/port'

params = {"code":"069500","date":"","sort":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'isin', type: 'String', description: '표준코드' },
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'kr_name', type: 'String', description: '한글 종목명' },
      { name: 'constituents', type: 'Number', description: '구성 종목수' },
      { name: 'admin_number', type: 'String', description: '사무수탁사 번호' },
      { name: 'etf_value', type: 'Number', description: '전체 설정금액' },
      { name: 'port_isin', type: 'String', description: '구성종목 표준코드' },
      { name: 'port_code', type: 'String', description: '구성종목 코드' },
      { name: 'port_name', type: 'String', description: '구성 종목명' },
      { name: 'port_value', type: 'Number', description: '구성종목 설정금액' },
      { name: 'port_volume', type: 'Number', description: '구성종목 편입수량' }
    ]
  },

  // 지수 기본 정보 (새로 크롤링됨)
  'index/info': {
    url: '/api/index/info',
    title: '기본',
    isCrawled: true,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 지수코드 (복수 코드 조회시 ,로 구분)', example: 'KGG01P, K2G01P, QGG01P' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD) 미입력시 today-1', example: '20240712' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
# SSL 인증 처리 무효화
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/index/info'

params = {"code":"KGG01P, K2G01P, QGG01P","date":"20240712"}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

# 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'index_type', type: 'String', description: '지수 종류 구분' },
      { name: 'code', type: 'String', description: '지수 코드' },
      { name: 'kr_name', type: 'Number', description: '한글 지수명' },
      { name: 'open_price', type: 'Number', description: '시가' },
      { name: 'high_price', type: 'Number', description: '고가' },
      { name: 'low_price', type: 'Number', description: '저가' },
      { name: 'close_price', type: 'Number', description: '현재가' },
      { name: 'change', type: 'Number', description: '전일대비' },
      { name: 'change_rate', type: 'Number', description: '등락률' },
      { name: 'trading_volume', type: 'Number', description: '거래량 (천주)' },
      { name: 'trading_value', type: 'Number', description: '거래대금 (백만원)' },
      { name: 'marketcap', type: 'Number', description: '시가총액 (백만원)' },
      { name: 'constituents', type: 'Number', description: '구성종목수' },
      { name: 'traded_number', type: 'Number', description: '거래종목수' },
      { name: 'advanced_count', type: 'Number', description: '상승종목수' },
      { name: 'declined_count', type: 'Number', description: '하락종목수' },
      { name: 'equal_count', type: 'Number', description: '보합종목수' },
      { name: 'advanced_volume', type: 'Number', description: '상승주수 (천주)' },
      { name: 'declined_volume', type: 'Number', description: '하락주수 (천주)' },
      { name: 'equal_volume', type: 'Number', description: '보합주수 (천주)' },
      { name: 'advanced_value', type: 'Number', description: '상승금액 (백만원)' },
      { name: 'declined_value', type: 'Number', description: '하락금액 (백만원)' },
      { name: 'equal_value', type: 'Number', description: '보합금액 (백만원)' }
    ]
  },

  // ========== ETF 추가 API들 (자동 생성) ==========
  'etf/search': {
    url: '/api/etf/search',
    title: '종목 보유 ETF 검색',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '종목코드', example: '005930' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/etf/search'

params = {"code":"005930","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'etf_code', type: 'String', description: 'ETF 코드' },
      { name: 'etf_name', type: 'String', description: 'ETF 명' },
      { name: 'holding_ratio', type: 'Number', description: '보유비중' }
    ]
  },

  // ========== ETP API들 (자동 생성) ==========
  'etp': {
    url: '/api/etp',
    title: 'ETP 추가정보',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: 'ETP 종목코드', example: '091160' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/etp'

params = {"code":"091160","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'name', type: 'String', description: '종목명' },
      { name: 'nav', type: 'Number', description: 'NAV' },
      { name: 'tracking_error', type: 'Number', description: '추적오차' }
    ]
  },

  'etp/list': {
    url: '/api/etp/list',
    title: 'ETP-상세검색',
    isCrawled: false,
    parameters: [
      { name: 'name', type: 'String', required: false, description: 'ETP명 검색' },
      { name: 'code', type: 'String', required: false, description: 'ETP 코드 검색' },
      { name: 'type', type: 'String', required: false, description: 'ETP 타입' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/etp/list'

params = {"name":"","code":"","type":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'name', type: 'String', description: '종목명' },
      { name: 'type', type: 'String', description: 'ETP 타입' }
    ]
  },

  // ========== 주식 추가 API들 (자동 생성) ==========
  'stock/tick': {
    url: '/api/stock/tick',
    title: '체결(정규장)',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' },
      { name: 'time', type: 'String', required: false, description: '조회시간 (HHMMSS)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/tick'

params = {"code":"005930","date":"","time":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'time', type: 'String', description: '체결시간' },
      { name: 'price', type: 'Number', description: '체결가격' },
      { name: 'volume', type: 'Number', description: '체결량' }
    ]
  },

  'stock/foreign': {
    url: '/api/stock/foreign',
    title: '외국인 지분율',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/foreign'

params = {"code":"005930","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'foreign_ratio', type: 'Number', description: '외국인 지분율' },
      { name: 'foreign_shares', type: 'Number', description: '외국인 보유주식수' }
    ]
  },

  'stock/rank': {
    url: '/api/stock/rank',
    title: '순위',
    isCrawled: false,
    parameters: [
      { name: 'type', type: 'String', required: false, description: '순위 타입', example: 'volume' },
      { name: 'market', type: 'String', required: false, description: '시장구분', example: 'KOSPI' },
      { name: 'count', type: 'Number', required: false, description: '조회 개수', example: '50' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/rank'

params = {"type":"volume","market":"KOSPI","count":"50"}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'rank', type: 'Number', description: '순위' },
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'name', type: 'String', description: '종목명' },
      { name: 'value', type: 'Number', description: '순위 기준값' }
    ]
  },

  'stock/investor': {
    url: '/api/stock/investor',
    title: '투자자-일별',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'startDate', type: 'Number', required: false, description: '시작일자 (YYYYMMDD)' },
      { name: 'endDate', type: 'Number', required: false, description: '종료일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/investor'

params = {"code":"005930","startDate":"","endDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'individual', type: 'Number', description: '개인 거래량' },
      { name: 'foreign', type: 'Number', description: '외국인 거래량' },
      { name: 'institution', type: 'Number', description: '기관 거래량' }
    ]
  },

  'stock/tick_etc': {
    url: '/api/stock/tick_etc',
    title: '체결(정규장 외)',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' },
      { name: 'session', type: 'String', required: false, description: '세션구분', example: 'PRE' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/tick_etc'

params = {"code":"005930","date":"","session":"PRE"}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'time', type: 'String', description: '체결시간' },
      { name: 'price', type: 'Number', description: '체결가격' },
      { name: 'session', type: 'String', description: '세션구분' }
    ]
  },

  'stock/lending': {
    url: '/api/stock/lending',
    title: '신용 거래',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/lending'

params = {"code":"005930","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'lending_balance', type: 'Number', description: '신용잔고' },
      { name: 'lending_volume', type: 'Number', description: '신용거래량' }
    ]
  },

  'stock/borrowing': {
    url: '/api/stock/borrowing',
    title: '대차 거래',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/borrowing'

params = {"code":"005930","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'borrowing_balance', type: 'Number', description: '대차잔고' },
      { name: 'borrowing_volume', type: 'Number', description: '대차거래량' }
    ]
  },

  'stock/expired': {
    url: '/api/stock/expired',
    title: '폐지종목',
    isCrawled: false,
    parameters: [
      { name: 'market', type: 'String', required: false, description: '시장구분', example: 'KOSPI' },
      { name: 'expired_date', type: 'Number', required: false, description: '폐지일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/expired'

params = {"market":"KOSPI","expired_date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'name', type: 'String', description: '종목명' },
      { name: 'expired_date', type: 'Number', description: '폐지일자' }
    ]
  },

  'stock/comp': {
    url: '/api/stock/comp',
    title: '개요 및 재무상태표',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 종목코드', example: '005930' },
      { name: 'year', type: 'Number', required: false, description: '조회년도 (YYYY)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/stock/comp'

params = {"code":"005930","year":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '종목코드' },
      { name: 'company_name', type: 'String', description: '회사명' },
      { name: 'revenue', type: 'Number', description: '매출액' },
      { name: 'profit', type: 'Number', description: '순이익' }
    ]
  },

  // ========== 지수 추가 API들 (자동 생성) ==========
  'index/hist': {
    url: '/api/index/hist',
    title: '일별',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 지수코드', example: 'KGG01P' },
      { name: 'startDate', type: 'Number', required: false, description: '시작일자 (YYYYMMDD)' },
      { name: 'endDate', type: 'Number', required: false, description: '종료일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/index/hist'

params = {"code":"KGG01P","startDate":"","endDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'code', type: 'String', description: '지수코드' },
      { name: 'close_price', type: 'Number', description: '종가' },
      { name: 'change_rate', type: 'Number', description: '등락률' }
    ]
  },

  'index/investor/intra': {
    url: '/api/index/investor/intra',
    title: '투자자-일중',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 지수코드', example: 'KGG01P' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/index/investor/intra'

params = {"code":"KGG01P","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'time', type: 'String', description: '시간' },
      { name: 'individual', type: 'Number', description: '개인 거래량' },
      { name: 'foreign', type: 'Number', description: '외국인 거래량' },
      { name: 'institution', type: 'Number', description: '기관 거래량' }
    ]
  },

  'index/investor/hist': {
    url: '/api/index/investor/hist',
    title: '투자자-일별',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 지수코드', example: 'KGG01P' },
      { name: 'startDate', type: 'Number', required: false, description: '시작일자 (YYYYMMDD)' },
      { name: 'endDate', type: 'Number', required: false, description: '종료일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/index/investor/hist'

params = {"code":"KGG01P","startDate":"","endDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'individual', type: 'Number', description: '개인 거래량' },
      { name: 'foreign', type: 'Number', description: '외국인 거래량' },
      { name: 'institution', type: 'Number', description: '기관 거래량' }
    ]
  },

  'index/constituents': {
    url: '/api/index/constituents',
    title: '구성 종목',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '6자리 지수코드', example: 'KGG01P' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/index/constituents'

params = {"code":"KGG01P","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'constituent_code', type: 'String', description: '구성종목코드' },
      { name: 'constituent_name', type: 'String', description: '구성종목명' },
      { name: 'weight', type: 'Number', description: '비중' }
    ]
  },

  // ========== 선물 추가 API들 (자동 생성) ==========
  'future/info': {
    url: '/api/future/info',
    title: '기본',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '선물 종목코드', example: '101V6000' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/info'

params = {"code":"101V6000","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '선물코드' },
      { name: 'name', type: 'String', description: '선물명' },
      { name: 'current_price', type: 'Number', description: '현재가' },
      { name: 'underlying_price', type: 'Number', description: '기초자산가격' }
    ]
  },

  'future/tick': {
    url: '/api/future/tick',
    title: '체결',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '선물 종목코드', example: '101V6000' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/tick'

params = {"code":"101V6000","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'time', type: 'String', description: '체결시간' },
      { name: 'price', type: 'Number', description: '체결가격' },
      { name: 'volume', type: 'Number', description: '체결량' }
    ]
  },

  'future/investor/hist': {
    url: '/api/future/investor/hist',
    title: '투자자-일별',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '선물 종목코드', example: '101V6000' },
      { name: 'startDate', type: 'Number', required: false, description: '시작일자 (YYYYMMDD)' },
      { name: 'endDate', type: 'Number', required: false, description: '종료일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/investor/hist'

params = {"code":"101V6000","startDate":"","endDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'individual', type: 'Number', description: '개인 거래량' },
      { name: 'foreign', type: 'Number', description: '외국인 거래량' }
    ]
  },

  'future/investor/intra': {
    url: '/api/future/investor/intra',
    title: '투자자-일중',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '선물 종목코드', example: '101V6000' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/investor/intra'

params = {"code":"101V6000","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'time', type: 'String', description: '시간' },
      { name: 'individual', type: 'Number', description: '개인 거래량' },
      { name: 'foreign', type: 'Number', description: '외국인 거래량' }
    ]
  },

  'future/underlying': {
    url: '/api/future/underlying',
    title: '기초자산코드',
    isCrawled: false,
    parameters: [
      { name: 'type', type: 'String', required: false, description: '기초자산 타입' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/future/underlying'

params = {"type":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'underlying_code', type: 'String', description: '기초자산코드' },
      { name: 'underlying_name', type: 'String', description: '기초자산명' }
    ]
  },

  // ========== 옵션 추가 API들 (자동 생성) ==========
  'option/info': {
    url: '/api/option/info',
    title: '기본',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '옵션 종목코드' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/option/info'

params = {"code":"","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'code', type: 'String', description: '옵션코드' },
      { name: 'strike_price', type: 'Number', description: '행사가' },
      { name: 'option_type', type: 'String', description: '옵션타입' }
    ]
  },

  'option/hist': {
    url: '/api/option/hist',
    title: '일별',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '옵션 종목코드' },
      { name: 'startDate', type: 'Number', required: false, description: '시작일자 (YYYYMMDD)' },
      { name: 'endDate', type: 'Number', required: false, description: '종료일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/option/hist'

params = {"code":"","startDate":"","endDate":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'date', type: 'Number', description: '일자' },
      { name: 'close_price', type: 'Number', description: '종가' },
      { name: 'volume', type: 'Number', description: '거래량' }
    ]
  },

  'option/tick': {
    url: '/api/option/tick',
    title: '체결',
    isCrawled: false,
    parameters: [
      { name: 'code', type: 'String', required: true, description: '옵션 종목코드' },
      { name: 'date', type: 'Number', required: false, description: '조회일자 (YYYYMMDD)' }
    ],
    pythonCode: `import sys, json, requests
session = requests.Session()
session.verify = False
api_url = 'https://infomaxy.einfomax.co.kr/api/option/tick'

params = {"code":"","date":""}
headers = {"Authorization" : 'bearer TOKEN'}
r = session.get(api_url, params = params, headers = headers)

print(json.dumps(r.json(), ensure_ascii=False, indent=2))`,
    outputFields: [
      { name: 'time', type: 'String', description: '체결시간' },
      { name: 'price', type: 'Number', description: '체결가격' },
      { name: 'volume', type: 'Number', description: '체결량' }
    ]
  }
}

// URL에서 크롤링 정보 가져오기
export function getCrawledApiInfo(urlPath: string): CrawledApiInfo | null {
  return crawledApiMapping[urlPath] || null
}

// 크롤링된 API인지 확인
export function isCrawledApi(urlPath: string): boolean {
  const info = getCrawledApiInfo(urlPath)
  return info?.isCrawled || false
}

// 비공개 API 태그 추가 함수
export function addPrivateTagIfNeeded(urlPath: string, tags: string[]): string[] {
  if (!isCrawledApi(urlPath) && !tags.includes('비공개')) {
    return [...tags, '비공개']
  }
  return tags
}

// 크롤링된 파라미터 정보 가져오기
export function getCrawledParameters(urlPath: string): CrawledParameter[] {
  const info = getCrawledApiInfo(urlPath)
  return info?.parameters || []
}

// 크롤링된 Python 코드 가져오기
export function getCrawledPythonCode(urlPath: string): string {
  const info = getCrawledApiInfo(urlPath)
  return info?.pythonCode || ''
}
