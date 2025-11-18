import mysql.connector
from mysql.connector import Error
import 

class MySQLDatabase:
    def __init__(self, host=None, user=None, password=None, database=None):
        # 직접 입력 없으면 env 값 사용
        self.host = host or os.getenv("MYSQL_HOST", "localhost")
        self.user = user or os.getenv("MYSQL_USER", "root")
        self.password = password or os.getenv("MYSQL_PASSWORD", "")
        self.database = database or os.getenv("MYSQL_DATABASE", "")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def execute(self, query, params=None, commit=False):
        """쿼리 실행"""
        self.connect()
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if commit:
                self.conn.commit()
            return cursor
        except Error as e:
            print(f"❌ 쿼리 실행 오류: {e}")
            raise e

    def fetchall(self, query, params=None):
        """조회용"""
        cursor = self.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetchone(self, query, params=None):
        """한 행 조회"""
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def close(self):
        """DB 연결 종료"""
        if self.conn:
            self.conn.close()
            self.conn = None