# 简单的 Python 后端服务器（使用 Flask）
# 安装依赖：pip install flask flask-cors flask-admin

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import pytz
import re
from sqlalchemy import text

app = Flask(__name__, static_folder='web')
CORS(app)

# 数据存储配置（ORM）
DATA_FILE = 'users.json'  # 仅用于历史回退；默认不再使用
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Flask-Admin 配置
app.config['SECRET_KEY'] = 'my-secret-key'  # 用于session和CSRF保护

# 导入数据模型和数据库实例
from models import db, Team, TeamMember, Config
db.init_app(app)
# 导入并设置Flask-Admin
from admin import setup_admin
# 设置Flask-Admin，但使用不同的URL前缀避免冲突
admin_instance = setup_admin(app)

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
                'createdAt': (team.createdAt.strftime('%Y-%m-%d %H:%M:%S') if team.createdAt else ''),
                'updatedAt': (team.updatedAt.strftime('%Y-%m-%d %H:%M:%S') if team.updatedAt else ''),
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
    # 使用上海时间
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    now_dt = datetime.now(shanghai_tz)
    
    try:
        # 检查团队名称是否已存在（通过team_name查找）
        existing_team = Team.query.filter_by(team_name=team_data.get('team_name', '')).first()
        
        if existing_team:
            # 团队名已存在，返回错误
            return False, "团队名称已存在，请使用其他名称"
        
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
        return False, f'保存团队数据失败: {str(e)}'

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
        # 首先检查报名截止时间
        deadline_config = get_config_by_key('DEADLINE')
        if deadline_config and deadline_config['type'] == 'datetime':
            # 获取当前时间（上海时区）
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(shanghai_tz)
            
            # 解析截止时间（get_config_by_key已经对时间类型做了转换）
            try:
                deadline_str = deadline_config['value']
                deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                # 设置为上海时区
                deadline_dt = shanghai_tz.localize(deadline_dt)
                
                # 比较时间
                if current_time > deadline_dt:
                    return jsonify({
                        'success': False,
                        'message': f'报名已截止，截止时间为：{deadline_str}'
                    }), 403
            except ValueError as e:
                print(f'解析截止时间失败: {e}')
                # 如果解析失败，允许继续提交（避免因配置错误导致系统无法使用）
        
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
        
        success, result = save_team(team_data, members_info)
        
        if success:
            return jsonify({
                'success': True,
                'message': '您已成功报名参加"码上AI·2025深信服CoStrict校园挑战赛"。我们已向您的邮箱发送确认邮件，请查收。',
                'team_id': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result
            }), 400

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
            'createdAt': (team.createdAt.strftime('%Y-%m-%d %H:%M:%S') if team.createdAt else ''),
            'updatedAt': (team.updatedAt.strftime('%Y-%m-%d %H:%M:%S') if team.updatedAt else ''),
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

def get_config_by_key(config_key):
    """
    根据配置键查询配置的最新记录，并根据类型返回对应格式的值
    
    Args:
        config_key (str): 配置键
        
    Returns:
        dict: 包含配置信息的字典，如果不存在则返回None
    """
    try:
        config = Config.query.filter_by(config_key=config_key).order_by(Config.updatedAt.desc()).first()
        if config:
            # 根据配置类型转换值
            value = config.config_value
            if config.config_type == 'int':
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    print(f'配置键 {config_key} 的值无法转换为整数，保持原字符串')
            elif config.config_type == 'datetime':
                try:
                    # 尝试解析日期时间字符串并转换为标准格式
                    from datetime import datetime
                    dt = datetime.fromisoformat(value) if value else None
                    value = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else value
                except (ValueError, TypeError):
                    print(f'配置键 {config_key} 的值无法转换为日期时间，保持原字符串')
            
            return {
                'key': config.config_key,
                'value': value,
                'type': config.config_type,
                'description': config.description
            }
        return None
    except Exception as e:
        print(f'查询配置错误: {e}')
        return None

@app.route('/api/config', methods=['GET'])
def get_config():
    """根据config_key查询配置项 - 供前端使用"""
    # 获取查询参数中的key
    config_key = request.args.get('config_key')
    
    if not config_key:
        return jsonify({
            'success': False,
            'message': '请提供配置键(key)参数'
        }), 400
    
    # 使用封装的查询函数
    result = get_config_by_key(config_key)
    
    if not result:
        return jsonify({
            'success': False,
            'message': '配置项不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': result
    })

if __name__ == '__main__':
    print('服务器启动中...')
    print('访问 http://localhost:5000 查看表单页面')
    
    # 初始化数据库，失败时退出
    if not init_db():
        print("数据库初始化失败，服务器无法启动")
        exit(1)
    
    # 根据环境变量决定是否启用调试模式
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)


