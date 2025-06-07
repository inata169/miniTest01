"""
カスタム例外クラス
"""


class WatchdogError(Exception):
    """ベース例外クラス"""
    pass


class CSVParseError(WatchdogError):
    """CSV解析エラー"""
    pass


class DataSourceError(WatchdogError):
    """データソースエラー"""
    pass


class DatabaseError(WatchdogError):
    """データベースエラー"""
    pass


class ConfigError(WatchdogError):
    """設定ファイルエラー"""
    pass


class NetworkError(DataSourceError):
    """ネットワークエラー"""
    pass


class AlertError(WatchdogError):
    """アラート送信エラー"""
    pass