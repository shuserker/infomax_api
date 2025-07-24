from posco_news_monitor import PoscoNewsMonitor
from datetime import datetime

# 테스트용 모니터 생성
monitor = PoscoNewsMonitor('test_webhook')

# 데이터 가져오기
data = monitor.get_news_data()

if data:
    # 메시지 생성
    message = "🔔 POSCO 뉴스 업데이트\n\n변경사항: 테스트\n\n"
    
    for news_type, news_data in data.items():
        title = news_data['title'][:60] + "..." if len(news_data['title']) > 60 else news_data['title']
        message += f"📰 {news_type.upper()}\n"
        message += f"제목: {title}\n"
        message += f"날짜: {news_data['date']} {news_data['time']}\n"
        message += f"작성자: {', '.join(news_data['writer'])}\n\n"
    
    message += f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print("=" * 50)
    print("Dooray 메시지 미리보기:")
    print("=" * 50)
    print(message)
    print("=" * 50)
else:
    print("❌ 데이터를 가져올 수 없습니다.")