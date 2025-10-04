// 대량 API 크롤링 시스템
// 모든 API 문서를 체계적으로 크롤링하여 매핑 정보를 생성

import { correctApiPackagesData } from '../data/correctApiData'

// 크롤링할 API URL 목록 생성
export function generateCrawlingUrls(): string[] {
  const baseDocUrl = 'https://infomaxapi.einfomax.co.kr/docs/'
  
  // 모든 API 패키지에서 URL 패스 추출
  const urlPaths = correctApiPackagesData.map(([, , urlPath]) => urlPath as string)
  
  // 중복 제거 (혹시 중복이 있을 수 있음)
  const uniquePaths = [...new Set(urlPaths)]
  
  // 전체 크롤링 URL 생성
  const crawlingUrls = uniquePaths.map(path => `${baseDocUrl}${path}`)
  
  console.log(`🔍 생성된 크롤링 URL 목록 (${crawlingUrls.length}개):`)
  crawlingUrls.forEach((url, index) => {
    console.log(`${index + 1}. ${url}`)
  })
  
  return crawlingUrls
}

// 크롤링 대상 URL 목록 (95개)
export const CRAWLING_TARGET_URLS = [
  // KRX-증시-ETF
  'https://infomaxapi.einfomax.co.kr/docs/etf/intra',
  'https://infomaxapi.einfomax.co.kr/docs/etf/port', 
  'https://infomaxapi.einfomax.co.kr/docs/etf/hist',
  'https://infomaxapi.einfomax.co.kr/docs/etf/search',
  
  // KRX-증시-ETP
  'https://infomaxapi.einfomax.co.kr/docs/etp',
  'https://infomaxapi.einfomax.co.kr/docs/etp/list',
  
  // KRX-증시-주식
  'https://infomaxapi.einfomax.co.kr/docs/stock/code',
  'https://infomaxapi.einfomax.co.kr/docs/stock/info',
  'https://infomaxapi.einfomax.co.kr/docs/stock/hist',
  'https://infomaxapi.einfomax.co.kr/docs/stock/tick',
  'https://infomaxapi.einfomax.co.kr/docs/stock/foreign',
  'https://infomaxapi.einfomax.co.kr/docs/stock/rank',
  'https://infomaxapi.einfomax.co.kr/docs/stock/investor',
  'https://infomaxapi.einfomax.co.kr/docs/stock/tick_etc',
  'https://infomaxapi.einfomax.co.kr/docs/stock/lending',
  'https://infomaxapi.einfomax.co.kr/docs/stock/borrowing',
  'https://infomaxapi.einfomax.co.kr/docs/stock/expired',
  
  // KRX-증시-지수
  'https://infomaxapi.einfomax.co.kr/docs/index/code',
  'https://infomaxapi.einfomax.co.kr/docs/index/info',
  'https://infomaxapi.einfomax.co.kr/docs/index/hist',
  'https://infomaxapi.einfomax.co.kr/docs/index/investor/intra',
  'https://infomaxapi.einfomax.co.kr/docs/index/investor/hist',
  'https://infomaxapi.einfomax.co.kr/docs/index/constituents',
  
  // KRX-파생-선물
  'https://infomaxapi.einfomax.co.kr/docs/future/code',
  'https://infomaxapi.einfomax.co.kr/docs/future/info',
  'https://infomaxapi.einfomax.co.kr/docs/future/hist',
  'https://infomaxapi.einfomax.co.kr/docs/future/tick',
  'https://infomaxapi.einfomax.co.kr/docs/future/investor/hist',
  'https://infomaxapi.einfomax.co.kr/docs/future/investor/intra',
  'https://infomaxapi.einfomax.co.kr/docs/future/underlying',
  'https://infomaxapi.einfomax.co.kr/docs/future/active',
  'https://infomaxapi.einfomax.co.kr/docs/future/expired',
  'https://infomaxapi.einfomax.co.kr/docs/future/2active',
  
  // KRX-파생-옵션
  'https://infomaxapi.einfomax.co.kr/docs/option/code',
  'https://infomaxapi.einfomax.co.kr/docs/option/info',
  'https://infomaxapi.einfomax.co.kr/docs/option/hist',
  'https://infomaxapi.einfomax.co.kr/docs/option/tick',
  'https://infomaxapi.einfomax.co.kr/docs/option/greeks/intra',
  'https://infomaxapi.einfomax.co.kr/docs/option/greeks/hist',
  'https://infomaxapi.einfomax.co.kr/docs/option/investor/intra',
  'https://infomaxapi.einfomax.co.kr/docs/option/investor/hist',
  'https://infomaxapi.einfomax.co.kr/docs/option/active',
  'https://infomaxapi.einfomax.co.kr/docs/option/underlying',
  
  // 경제지표
  'https://infomaxapi.einfomax.co.kr/docs/eco/hist',
  
  // 기업정보
  'https://infomaxapi.einfomax.co.kr/docs/stock/comp',
  
  // 기업정보-한국
  'https://infomaxapi.einfomax.co.kr/docs/company/listed',
  'https://infomaxapi.einfomax.co.kr/docs/company/external',
  'https://infomaxapi.einfomax.co.kr/docs/company/detailaccout',
  'https://infomaxapi.einfomax.co.kr/docs/company/accout',
  
  // 뉴스
  'https://infomaxapi.einfomax.co.kr/docs/news/search',
  'https://infomaxapi.einfomax.co.kr/docs/news/view',
  
  // 리서치리포트
  'https://infomaxapi.einfomax.co.kr/docs/report/list',
  'https://infomaxapi.einfomax.co.kr/docs/report/korea',
  
  // 외환
  'https://infomaxapi.einfomax.co.kr/docs/fx/exchangerate/intra',
  'https://infomaxapi.einfomax.co.kr/docs/fx/exchangerate/hist',
  'https://infomaxapi.einfomax.co.kr/docs/fx/info',
  'https://infomaxapi.einfomax.co.kr/docs/fx/hist',
  'https://infomaxapi.einfomax.co.kr/docs/fx/code',
  'https://infomaxapi.einfomax.co.kr/docs/fx/intra',
  'https://infomaxapi.einfomax.co.kr/docs/fx/mar',
  
  // 외환-CNHKRW
  'https://infomaxapi.einfomax.co.kr/docs/cnhkrw/smb',
  'https://infomaxapi.einfomax.co.kr/docs/cnhkrw/kmb',
  'https://infomaxapi.einfomax.co.kr/docs/cnhkrw/tick',
  
  // 외환-USDKRW
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/smb',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/kmb',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/kmb/volumeattime',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/bestattime',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/smb/volumeattime',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/tick',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/smb1530',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/kmb1530',
  
  // 외환-USDKRW 비공개
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/smb/tick',
  'https://infomaxapi.einfomax.co.kr/docs/usdkrw/kmb/tick',
  
  // 외환-USDKRW포워드
  'https://infomaxapi.einfomax.co.kr/docs/usdkrwforward/tick',
  
  // 차트
  'https://infomaxapi.einfomax.co.kr/docs/chart/all',
  
  // 채권
  'https://infomaxapi.einfomax.co.kr/docs/bond/basic_info', // ✅ 이미 크롤링 완료
  'https://infomaxapi.einfomax.co.kr/docs/bond/marketvalue',
  'https://infomaxapi.einfomax.co.kr/docs/bond/cashflow',
  'https://infomaxapi.einfomax.co.kr/docs/bond/marketvaluation', // ✅ 이미 크롤링 완료
  
  // 채권 - 발행기관 관련
  'https://infomaxapi.einfomax.co.kr/docs/bond/corp_name',
  
  // 채권 통합 일중/일별 체결정보
  'https://infomaxapi.einfomax.co.kr/docs/bond/market/mn_hist', // ✅ 이미 크롤링 완료
  
  // 채권-금리/수익률
  'https://infomaxapi.einfomax.co.kr/docs/bond/rate/ir_yield',
  
  // 채권-발행정보
  'https://infomaxapi.einfomax.co.kr/docs/bond/league',
  
  // 채권-장내국채
  'https://infomaxapi.einfomax.co.kr/docs/bond/jang/1',
  'https://infomaxapi.einfomax.co.kr/docs/bond/market/gov_hist',
  'https://infomaxapi.einfomax.co.kr/docs/bond/market/hoga_info',
  'https://infomaxapi.einfomax.co.kr/docs/bond/market/code_info',
  'https://infomaxapi.einfomax.co.kr/docs/bond/market/tick_info',
  'https://infomaxapi.einfomax.co.kr/docs/bond/market/hoga_real',
  
  // 채권-해외채권
  'https://infomaxapi.einfomax.co.kr/docs/bond/foreign/kp',
  
  // 파생-국채선물
  'https://infomaxapi.einfomax.co.kr/docs/future/basket'
]

export function getNextCrawlingBatch(batchSize: number = 5): string[] {
  // 이미 크롤링 완료된 URL들
  const completedUrls = [
    'https://infomaxapi.einfomax.co.kr/docs/bond/market/mn_hist',
    'https://infomaxapi.einfomax.co.kr/docs/bond/marketvaluation',
    'https://infomaxapi.einfomax.co.kr/docs/stock/hist',
    'https://infomaxapi.einfomax.co.kr/docs/stock/code',
    'https://infomaxapi.einfomax.co.kr/docs/bond/basic_info'
  ]
  
  // 미완료 URL들 중에서 배치 크기만큼 반환
  const remainingUrls = CRAWLING_TARGET_URLS.filter(url => !completedUrls.includes(url))
  return remainingUrls.slice(0, batchSize)
}

console.log(`📊 총 크롤링 대상: ${CRAWLING_TARGET_URLS.length}개 API`)
console.log(`✅ 완료된 크롤링: 5개 API`)  
console.log(`🔄 남은 크롤링: ${CRAWLING_TARGET_URLS.length - 5}개 API`)
