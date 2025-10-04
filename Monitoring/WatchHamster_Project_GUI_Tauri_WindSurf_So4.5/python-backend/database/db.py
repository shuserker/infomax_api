"""
SQLite 데이터베이스 관리
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite 데이터베이스 클래스"""
    
    def __init__(self, db_path: str = "watchhamster.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self.init_database()
    
    def connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # 회사 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    logo_url TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 웹훅 설정 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT NOT NULL,
                    channel_name TEXT NOT NULL,
                    webhook_url TEXT NOT NULL,
                    bot_name TEXT NOT NULL,
                    bot_icon TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, channel_name)
                )
            """)
            
            # API 설정 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT NOT NULL,
                    api_name TEXT NOT NULL,
                    api_url TEXT NOT NULL,
                    api_token TEXT,
                    config TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, api_name)
                )
            """)
            
            # 웹훅 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook_logs (
                    id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_type TEXT NOT NULL,
                    bot_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message_id TEXT,
                    error_message TEXT,
                    full_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)
            
            # 인덱스 생성
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhook_logs_company ON webhook_logs(company_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhook_logs_timestamp ON webhook_logs(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhook_logs_status ON webhook_logs(status)")
            
            conn.commit()
            logger.info("데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            conn.rollback()
            raise
        finally:
            self.close()
    
    # ========== 회사 관리 ==========
    
    def create_company(self, company_data: Dict[str, Any]) -> str:
        """회사 생성"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO companies (id, name, display_name, logo_url, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                company_data['id'],
                company_data['name'],
                company_data['display_name'],
                company_data.get('logo_url'),
                company_data.get('is_active', True)
            ))
            
            conn.commit()
            logger.info(f"회사 생성 완료: {company_data['id']}")
            return company_data['id']
            
        except sqlite3.IntegrityError:
            raise ValueError(f"회사 ID '{company_data['id']}'가 이미 존재합니다")
        except Exception as e:
            conn.rollback()
            logger.error(f"회사 생성 실패: {e}")
            raise
        finally:
            self.close()
    
    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """회사 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        finally:
            self.close()
    
    def get_all_companies(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """전체 회사 목록 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute("SELECT * FROM companies WHERE is_active = 1 ORDER BY name")
            else:
                cursor.execute("SELECT * FROM companies ORDER BY name")
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        finally:
            self.close()
    
    def update_company(self, company_id: str, update_data: Dict[str, Any]) -> bool:
        """회사 정보 수정"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            fields = []
            values = []
            
            for key, value in update_data.items():
                if key in ['name', 'display_name', 'logo_url', 'is_active']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(company_id)
            
            query = f"UPDATE companies SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            logger.info(f"회사 수정 완료: {company_id}")
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"회사 수정 실패: {e}")
            raise
        finally:
            self.close()
    
    def delete_company(self, company_id: str) -> bool:
        """회사 삭제"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
            conn.commit()
            logger.info(f"회사 삭제 완료: {company_id}")
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"회사 삭제 실패: {e}")
            raise
        finally:
            self.close()
    
    # ========== 웹훅 설정 관리 ==========
    
    def create_webhook_config(self, config_data: Dict[str, Any]) -> int:
        """웹훅 설정 생성"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO webhook_configs 
                (company_id, channel_name, webhook_url, bot_name, bot_icon, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                config_data['company_id'],
                config_data['channel_name'],
                config_data['webhook_url'],
                config_data['bot_name'],
                config_data['bot_icon'],
                config_data.get('is_active', True)
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            conn.rollback()
            logger.error(f"웹훅 설정 생성 실패: {e}")
            raise
        finally:
            self.close()
    
    def get_webhook_configs(self, company_id: str) -> List[Dict[str, Any]]:
        """회사별 웹훅 설정 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM webhook_configs 
                WHERE company_id = ? AND is_active = 1
            """, (company_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        finally:
            self.close()
    
    def get_webhook_config_by_channel(self, company_id: str, channel_name: str) -> Optional[Dict[str, Any]]:
        """채널별 웹훅 설정 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM webhook_configs 
                WHERE company_id = ? AND channel_name = ? AND is_active = 1
            """, (company_id, channel_name))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        finally:
            self.close()
    
    # ========== API 설정 관리 ==========
    
    def create_api_config(self, config_data: Dict[str, Any]) -> int:
        """API 설정 생성"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO api_configs 
                (company_id, api_name, api_url, api_token, config, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                config_data['company_id'],
                config_data['api_name'],
                config_data['api_url'],
                config_data.get('api_token'),
                json.dumps(config_data.get('config', {})),
                config_data.get('is_active', True)
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            conn.rollback()
            logger.error(f"API 설정 생성 실패: {e}")
            raise
        finally:
            self.close()
    
    def get_api_configs(self, company_id: str) -> List[Dict[str, Any]]:
        """회사별 API 설정 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM api_configs 
                WHERE company_id = ? AND is_active = 1
            """, (company_id,))
            
            rows = cursor.fetchall()
            configs = []
            for row in rows:
                config = dict(row)
                if config.get('config'):
                    config['config'] = json.loads(config['config'])
                configs.append(config)
            return configs
            
        finally:
            self.close()
    
    # ========== 웹훅 로그 관리 ==========
    
    def create_webhook_log(self, log_data: Dict[str, Any]) -> str:
        """웹훅 로그 생성"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO webhook_logs 
                (id, company_id, message_type, bot_type, priority, endpoint, 
                 status, message_id, error_message, full_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_data['id'],
                log_data['company_id'],
                log_data['message_type'],
                log_data['bot_type'],
                log_data['priority'],
                log_data['endpoint'],
                log_data['status'],
                log_data.get('message_id'),
                log_data.get('error_message'),
                log_data.get('full_message'),
                json.dumps(log_data.get('metadata', {}))
            ))
            
            conn.commit()
            return log_data['id']
            
        except Exception as e:
            conn.rollback()
            logger.error(f"웹훅 로그 생성 실패: {e}")
            raise
        finally:
            self.close()
    
    def get_webhook_logs(
        self, 
        company_id: Optional[str] = None,
        limit: int = 100,
        message_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """웹훅 로그 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM webhook_logs WHERE 1=1"
            params = []
            
            if company_id:
                query += " AND company_id = ?"
                params.append(company_id)
            
            if message_type:
                query += " AND message_type = ?"
                params.append(message_type)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                log = dict(row)
                if log.get('metadata'):
                    log['metadata'] = json.loads(log['metadata'])
                logs.append(log)
            return logs
            
        finally:
            self.close()
    
    def get_webhook_stats(self, company_id: Optional[str] = None) -> Dict[str, Any]:
        """웹훅 통계 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    COUNT(*) as total_sent,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_sends,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_sends,
                    MAX(timestamp) as last_send_time
                FROM webhook_logs
            """
            
            params = []
            if company_id:
                query += " WHERE company_id = ?"
                params.append(company_id)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            return {
                'total_sent': row['total_sent'] or 0,
                'successful_sends': row['successful_sends'] or 0,
                'failed_sends': row['failed_sends'] or 0,
                'retry_attempts': 0,
                'average_response_time': 0.0,
                'last_send_time': row['last_send_time']
            }
            
        finally:
            self.close()
    
    def delete_all_logs(self, company_id: Optional[str] = None) -> int:
        """로그 삭제"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if company_id:
                cursor.execute("DELETE FROM webhook_logs WHERE company_id = ?", (company_id,))
            else:
                cursor.execute("DELETE FROM webhook_logs")
            
            conn.commit()
            return cursor.rowcount
            
        except Exception as e:
            conn.rollback()
            logger.error(f"로그 삭제 실패: {e}")
            raise
        finally:
            self.close()


# 싱글톤 인스턴스
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """데이터베이스 인스턴스 가져오기"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
