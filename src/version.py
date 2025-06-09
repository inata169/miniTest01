#!/usr/bin/env python3
"""
バージョン管理モジュール
"""
import os

def get_version():
    """バージョン情報を取得"""
    try:
        version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return "1.0.0"

def get_version_info():
    """詳細なバージョン情報を取得"""
    version = get_version()
    parts = version.split('.')
    
    return {
        'version': version,
        'major': int(parts[0]) if len(parts) > 0 else 1,
        'minor': int(parts[1]) if len(parts) > 1 else 0,
        'patch': int(parts[2]) if len(parts) > 2 else 0,
        'release_name': get_release_name(version)
    }

def get_release_name(version):
    """バージョンに応じたリリース名を取得"""
    release_names = {
        '1.0.0': 'Initial Release',
        '1.1.0': 'Alert & Sort Enhancement',
        '1.2.0': 'Advanced Monitoring',
        '2.0.0': 'Major Upgrade'
    }
    return release_names.get(version, 'Development Version')

# バージョン定数
VERSION = get_version()
VERSION_INFO = get_version_info()

if __name__ == "__main__":
    info = get_version_info()
    print(f"Version: {info['version']}")
    print(f"Release: {info['release_name']}")
    print(f"Major.Minor.Patch: {info['major']}.{info['minor']}.{info['patch']}")