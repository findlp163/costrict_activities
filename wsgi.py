"""
WSGI入口文件，用于生产环境部署
"""

from server import app, init_db
from models import db
import os

def create_app():
    """创建并配置应用实例"""
    # 初始化数据库
    if not init_db():
        print("数据库初始化失败，应用无法启动")
        exit(1)
    
    # 初始化数据库
    with app.app_context():
        db.create_all()
    
    return app

# 应用工厂函数
application = create_app()

if __name__ == "__main__":
    # 仅在直接运行此文件时使用开发服务器
    application.run(debug=False, host='0.0.0.0', port=5000)