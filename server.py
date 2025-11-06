# 简单的 Python 后端服务器（使用 Flask）
# 安装依赖：pip install flask flask-cors

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime
import re
from sqlalchemy import text

app = Flask(__name__, static_folder='web')
CORS(app)

# 数据存储配置（ORM）
DATA_FILE = 'users.json'  # 仅用于历史回退；默认不再使用
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///users2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Team(db.Model):
    __tablename__ = 'teams'
    # 自增整型主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 
    
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
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 提交时间
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)  # 最新提交时间
    
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

def init_db():
    """改进的数据库初始化"""
    try:
        # 测试数据库连接
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            # 创建表
            db.create_all()
            print("数据库初始化成功")
            return True
    except Exception as e:
        print(f'数据库初始化失败: {e}')
        return False

def read_teams():
    """读取所有团队信息（ORM）"""
    try:
        teams = Team.query.order_by(Team.createdAt.desc()).all()
        result = []
        for team in teams:
            team_data = {
                'id': team.id,
                'createdAt': (team.createdAt.isoformat() if team.createdAt else ''),
                'updatedAt': (team.updatedAt.isoformat() if team.updatedAt else ''),
                'team_name': team.team_name,
                'competition_track': team.competition_track,
                'project_name': team.project_name,
                'repo_url': team.repo_url or '',
                'costrict_uid': team.costrict_uid,
                'project_intro': team.project_intro or '',
                'tech_solution': team.tech_solution or '',
                'goals_and_outlook': team.goals_and_outlook or '',
                'members': []
            }
            
            # 添加团队成员信息
            for member in team.members:
                team_data['members'].append({
                    'id': member.id,
                    'name': member.name,
                    'is_captain': member.is_captain,
                    'school': member.school,
                    'department': member.department,
                    'major_grade': member.major_grade,
                    'phone': member.phone,
                    'email': member.email,
                    'student_id': member.student_id or '',
                    'role': member.role,
                    'tech_stack': member.tech_stack or ''
                })
            
            result.append(team_data)
        return result
    except Exception as e:
        print(f'读取团队数据失败: {e}')
        return []

def save_team(team_data, members_data):
    """保存团队和成员数据"""
    now_dt = datetime.utcnow()
    
    try:
        # 检查团队名称是否已存在（通过team_name查找）
        existing_team = Team.query.filter_by(team_name=team_data.get('team_name', '')).first()
        
        if existing_team:
            # 更新现有团队信息
            existing_team.updatedAt = now_dt
            existing_team.competition_track = team_data.get('competition_track', '')
            existing_team.project_name = team_data.get('project_name', '')
            existing_team.repo_url = team_data.get('repo_url', '')
            existing_team.costrict_uid = team_data.get('costrict_uid', '')
            existing_team.project_intro = team_data.get('project_intro', '')
            existing_team.tech_solution = team_data.get('tech_solution', '')
            existing_team.goals_and_outlook = team_data.get('goals_and_outlook', '')
            
            # 删除现有成员（级联删除）
            TeamMember.query.filter_by(team_id=existing_team.id).delete()
            
            # 添加新成员
            for member_data in members_data:
                member = TeamMember(
                    team_id=existing_team.id,
                    team_name=team_data.get('team_name', ''),
                    name=member_data.get('name', ''),
                    is_captain=member_data.get('is_captain', False),
                    school=member_data.get('school', ''),
                    department=member_data.get('department', ''),
                    major_grade=member_data.get('major_grade', ''),
                    phone=member_data.get('phone', ''),
                    email=member_data.get('email', ''),
                    student_id=member_data.get('student_id', ''),
                    role=member_data.get('role', ''),
                    tech_stack=member_data.get('tech_stack', ''),
                    createdAt=now_dt,
                    updatedAt=now_dt
                )
                db.session.add(member)
            
            db.session.commit()
            return True, existing_team.id
        else:
            # 创建新团队
            new_team = Team(
                team_name=team_data.get('team_name', ''),
                competition_track=team_data.get('competition_track', ''),
                project_name=team_data.get('project_name', ''),
                repo_url=team_data.get('repo_url', ''),
                costrict_uid=team_data.get('costrict_uid', ''),
                project_intro=team_data.get('project_intro', ''),
                tech_solution=team_data.get('tech_solution', ''),
                goals_and_outlook=team_data.get('goals_and_outlook', ''),
                createdAt=now_dt,
                updatedAt=now_dt
            )
            db.session.add(new_team)
            db.session.flush()  # 获取新团队ID
            
            # 添加团队成员
            for member_data in members_data:
                member = TeamMember(
                    team_id=new_team.id,
                    team_name=team_data.get('team_name', ''),
                    name=member_data.get('name', ''),
                    is_captain=member_data.get('is_captain', False),
                    school=member_data.get('school', ''),
                    department=member_data.get('department', ''),
                    major_grade=member_data.get('major_grade', ''),
                    phone=member_data.get('phone', ''),
                    email=member_data.get('email', ''),
                    student_id=member_data.get('student_id', ''),
                    role=member_data.get('role', ''),
                    tech_stack=member_data.get('tech_stack', ''),
                    createdAt=now_dt,
                    updatedAt=now_dt
                )
                db.session.add(member)
            
            db.session.commit()
            return True, new_team.id
    except Exception as e:
        db.session.rollback()
        print(f'保存团队数据失败: {e}')
        return False, None

@app.route('/')
def index():
    """返回主页面"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """静态文件服务"""
    return send_from_directory('web', path)

@app.route('/api/team/submit', methods=['POST'])
def submit_team():
    """处理团队信息和成员提交"""
    try:
        data = request.get_json() or {}
        print(f'收到团队提交: {data}')

        # 验证团队信息
        team_info = data.get('team_info', {})
        members_info = data.get('members', [])
        
        # ===== 团队必填字段验证 =====
        team_name = str(team_info.get('team_name', '')).strip()
        competition_track = str(team_info.get('competition_track', '')).strip()
        project_name = str(team_info.get('project_name', '')).strip()
        costrict_uid = str(team_info.get('costrict_uid', '')).strip()
        
        if not all([team_name, competition_track, project_name, costrict_uid]):
            return jsonify({
                'success': False,
                'message': '请填写所有团队必填字段（团队名称、参赛赛道、作品名称、CoStrict UID）'
            }), 400
        
        # 验证参赛赛道
        valid_tracks = ['技术挑战赛', '创新应用赛']
        if competition_track not in valid_tracks:
            return jsonify({
                'success': False,
                'message': '参赛赛道必须为"技术挑战赛"或"创新应用赛"'
            }), 400
        
        # 验证项目简介、技术方案、目标与展望的长度（200-500字）
        project_intro = str(team_info.get('project_intro', '')).strip()
        tech_solution = str(team_info.get('tech_solution', '')).strip()
        goals_and_outlook = str(team_info.get('goals_and_outlook', '')).strip()
        
        for field_name, field_value in [('项目简介', project_intro), ('技术方案', tech_solution), ('目标与展望', goals_and_outlook)]:
            if field_value and (len(field_value) < 200 or len(field_value) > 500):
                return jsonify({
                    'success': False,
                    'message': f'{field_name}长度必须在200-500字之间'
                }), 400
        
        # ===== 验证团队成员信息 =====
        if not members_info or len(members_info) == 0:
            return jsonify({
                'success': False,
                'message': '至少需要添加一名团队成员'
            }), 400
        
        # 检查是否有队长
        has_captain = any(member.get('is_captain', False) for member in members_info)
        if not has_captain:
            return jsonify({
                'success': False,
                'message': '团队必须指定一名队长'
            }), 400
        
        # 验证每个成员的必填字段
        for i, member in enumerate(members_info):
            name = str(member.get('name', '')).strip()
            school = str(member.get('school', '')).strip()
            department = str(member.get('department', '')).strip()
            major_grade = str(member.get('major_grade', '')).strip()
            phone = str(member.get('phone', '')).strip()
            email = str(member.get('email', '')).strip()
            role = str(member.get('role', '')).strip()
            
            if not all([name, school, department, major_grade, phone, email, role]):
                return jsonify({
                    'success': False,
                    'message': f'请填写成员{i+1}的所有必填字段（姓名、学校/单位、学院/系别、专业与年级、联系电话、电子邮箱、项目角色）'
                }), 400
            
            # 验证邮箱格式
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email):
                return jsonify({
                    'success': False,
                    'message': f'成员{i+1}的邮箱格式不正确'
                }), 400
            
            # 验证手机号格式
            cn_phone_regex = r'^1[3-9]\d{9}$'
            if not re.match(cn_phone_regex, phone):
                return jsonify({
                    'success': False,
                    'message': f'成员{i+1}的手机号格式不正确（需为大陆11位且以1开头）'
                }), 400
        
        # ===== 保存团队和成员信息 =====
        team_data = {
            'team_name': team_name,
            'competition_track': competition_track,
            'project_name': project_name,
            'repo_url': str(team_info.get('repo_url', '')).strip(),
            'costrict_uid': costrict_uid,
            'project_intro': project_intro,
            'tech_solution': tech_solution,
            'goals_and_outlook': goals_and_outlook
        }
        
        success, team_id = save_team(team_data, members_info)
        
        if success:
            return jsonify({
                'success': True,
                'message': '您已成功报名参加"码上AI·2025深信服CoStrict校园挑战赛"。我们已向您的邮箱发送确认邮件，请查收。',
                'team_id': team_id
            })
        else:
            return jsonify({
                'success': False,
                'message': '服务器错误，请稍后重试'
            }), 500

    except Exception as e:
        print(f'处理团队提交错误: {e}')
        return jsonify({
            'success': False,
            'message': '服务器错误'
        }), 500

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """获取所有团队信息（管理接口）"""
    teams = read_teams()
    return jsonify({
        'success': True,
        'data': teams,
        'count': len(teams)
    })

@app.route('/api/team/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """获取特定团队信息"""
    try:
        team = Team.query.get(team_id)
        if not team:
            return jsonify({
                'success': False,
                'message': '团队不存在'
            }), 404
        
        team_data = {
            'id': team.id,
            'createdAt': (team.createdAt.isoformat() if team.createdAt else ''),
            'updatedAt': (team.updatedAt.isoformat() if team.updatedAt else ''),
            'team_name': team.team_name,
            'competition_track': team.competition_track,
            'project_name': team.project_name,
            'repo_url': team.repo_url or '',
            'costrict_uid': team.costrict_uid,
            'project_intro': team.project_intro or '',
            'tech_solution': team.tech_solution or '',
            'goals_and_outlook': team.goals_and_outlook or '',
            'members': []
        }
        
        # 添加团队成员信息
        for member in team.members:
            team_data['members'].append({
                'id': member.id,
                'name': member.name,
                'is_captain': member.is_captain,
                'school': member.school,
                'department': member.department,
                'major_grade': member.major_grade,
                'phone': member.phone,
                'email': member.email,
                'student_id': member.student_id or '',
                'role': member.role,
                'tech_stack': member.tech_stack or ''
            })
        
        return jsonify({
            'success': True,
            'data': team_data
        })
    except Exception as e:
        print(f'获取团队信息错误: {e}')
        return jsonify({
            'success': False,
            'message': '服务器错误'
        }), 500

if __name__ == '__main__':
    print('服务器启动中...')
    print('访问 http://localhost:5000 查看表单页面')
    
    # 初始化数据库，失败时退出
    if not init_db():
        print("数据库初始化失败，服务器无法启动")
        exit(1)
        
    app.run(debug=True, host='0.0.0.0', port=5000)


