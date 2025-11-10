"""
数据模型定义
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

# 创建数据库实例
db = SQLAlchemy()

# 定义上海时区
TZ = pytz.timezone('Asia/Shanghai')

def get_current_time():
    return datetime.now(TZ)

class Team(db.Model):
    __tablename__ = 'teams'
    # 自增整型主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=get_current_time)
    updatedAt = db.Column(db.DateTime, nullable=False, default=get_current_time)
    
    def __init__(self, **kwargs):
        super(Team, self).__init__(**kwargs)
        self.updatedAt = get_current_time()
    
    def update_timestamps(self):
        self.updatedAt = get_current_time()
    
    # 团队基本信息
    team_name = db.Column(db.String(50), nullable=False, unique=True)  # 团队名称（唯一）
    competition_track = db.Column(db.String(50), nullable=False)  # 参赛赛道（技术挑战赛/创新应用赛）
    project_name = db.Column(db.String(50), nullable=False)  # 作品名称
    repo_url = db.Column(db.String(255))  # 代码仓库链接
    costrict_uid = db.Column(db.String(50), nullable=False)  # CoStrict UID
    
    # 项目详细信息
    project_intro = db.Column(db.Text)  # 项目简介 (200-500字)
    tech_solution = db.Column(db.Text)  # 技术方案 (200-500字)
    goals_and_outlook = db.Column(db.Text)  # 目标与展望 (200-500字)
    
    # 团队成员关系
    members = db.relationship('TeamMember', backref='team', lazy=True, cascade='all, delete-orphan')


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    # 自增整型主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=get_current_time)  # 提交时间
    updatedAt = db.Column(db.DateTime, nullable=False, default=get_current_time)  # 最新提交时间
    
    def __init__(self, **kwargs):
        super(TeamMember, self).__init__(**kwargs)
        self.updatedAt = get_current_time()
    
    def update_timestamps(self):
        self.updatedAt = get_current_time()
    
    # 关联团队
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    # 团队基本信息
    team_name = db.Column(db.String(50), nullable=False)  # 团队名称（冗余字段，便于查询）
    
    # 个人基本信息
    name = db.Column(db.String(100), nullable=False)  # 姓名
    is_captain = db.Column(db.Boolean, default=False)  # 是否为队长
    school = db.Column(db.String(200), nullable=False)  # 学校/单位
    department = db.Column(db.String(200), nullable=False)  # 学院/系别
    major_grade = db.Column(db.String(200), nullable=False)  # 专业与年级
    phone = db.Column(db.String(20), nullable=False)  # 联系电话
    email = db.Column(db.String(200), nullable=False)  # 电子邮箱
    student_id = db.Column(db.String(50))  # 学号（可选）
    
    # 项目角色
    role = db.Column(db.String(100), nullable=False)  # 项目角色
    tech_stack = db.Column(db.String(500))  # 技术栈/擅长领域


class Config(db.Model):
    """
    系统配置表 - 简单的key-value键值对存储
    用于存储系统全局配置信息
    """
    __tablename__ = 'configs'
    
    # 自增整型主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=get_current_time)
    updatedAt = db.Column(db.DateTime, nullable=False, default=get_current_time)
    
    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)
        self.updatedAt = get_current_time()
    
    def update_timestamps(self):
        self.updatedAt = get_current_time()
    
    # 配置键 - 唯一索引
    config_key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    
    # 配置值
    config_value = db.Column(db.Text, nullable=True)
    
    # 配置类型 - 支持int、datetime、str，默认为str
    config_type = db.Column(db.Enum('str', 'int', 'datetime', name='config_type_enum'), nullable=False, default='str')
    
    # 配置描述
    description = db.Column(db.String(255), nullable=True)