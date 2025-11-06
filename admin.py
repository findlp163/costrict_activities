"""
Flask-Admin配置文件
定义管理界面的模型视图和自定义行为
"""

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, abort, Response
from models import db, Team, TeamMember


class MyAdminIndexView(AdminIndexView):
    """
    自定义管理界面首页视图
    """
    @expose('/')
    def index(self):
        # 这里可以添加自定义的首页逻辑
        return super(MyAdminIndexView, self).index()


class TeamView(ModelView):
    """
    团队模型的管理视图 - 简化配置，显示所有字段
    """
    # 启用列表页面的详情查看功能
    can_view_details = True
    
    # 启用导出功能
    can_export = True
    
    def on_model_change(self, form, model, is_created):
        """在模型保存前调用，自动更新时间戳"""
        if not is_created:
            # 更新现有记录时，手动更新时间戳
            model.update_timestamps()
        return super(TeamView, self).on_model_change(form, model, is_created)
    
    # 指定列表页面显示的字段
    column_list = ('id', 'createdAt', 'updatedAt', 'team_name', 'competition_track', 
                  'project_name', 'repo_url', 'costrict_uid')
    
    # 定义搜索字段
    column_searchable_list = ('team_name', 'project_name', 'competition_track')
    
    # 定义过滤器
    column_filters = ('competition_track', 'createdAt', 'updatedAt')
    
    # 自定义显示名称 - 中文字段标题
    column_labels = {
        'id': 'ID',
        'team_name': '团队名称',
        'competition_track': '参赛赛道',
        'project_name': '作品名称',
        'repo_url': '代码仓库链接',
        'costrict_uid': 'CoStrict 用户ID',
        'project_intro': '项目简介',
        'tech_solution': '技术方案',
        'goals_and_outlook': '目标与展望',
        'createdAt': '创建时间',
        'updatedAt': '更新时间'
    }


class TeamMemberView(ModelView):
    """
    团队成员模型的管理视图 - 简化配置，显示所有字段
    """
    # 启用列表页面的详情查看功能
    can_view_details = True
    
    # 启用导出功能
    can_export = True
    
    def on_model_change(self, form, model, is_created):
        """在模型保存前调用，自动更新时间戳"""
        if not is_created:
            # 更新现有记录时，手动更新时间戳
            model.update_timestamps()
        return super(TeamMemberView, self).on_model_change(form, model, is_created)
    
    # 指定列表页面显示的字段
    column_list = ('id', 'team_id', 'team_name', 'name', 'is_captain', 'school',
                  'department', 'major_grade', 'phone', 'email', 'student_id',
                  'role', 'tech_stack', 'createdAt', 'updatedAt')
    
    # 指定表单中显示的字段
    form_columns = ('team_id', 'team_name', 'name', 'is_captain', 'school',
                   'department', 'major_grade', 'phone', 'email', 'student_id',
                   'role', 'tech_stack')
    
    # 指定详情页面显示的字段
    column_details_list = ('id', 'team_id', 'team_name', 'name', 'is_captain', 'school',
                          'department', 'major_grade', 'phone', 'email', 'student_id',
                          'role', 'tech_stack', 'createdAt', 'updatedAt')
    
    # 定义搜索字段
    column_searchable_list = ('name', 'school', 'phone', 'email', 'team_name', 'tech_stack')
    
    # 定义过滤器
    column_filters = ('is_captain', 'school', 'phone', 'email', 'team_name', 'tech_stack')
    
    # 自定义显示名称 - 中文字段标题
    column_labels = {
        'id': 'ID',
        'team_id': '团队ID',
        'team_name': '团队名称',
        'name': '姓名',
        'is_captain': '是否为队长',
        'school': '学校/单位',
        'department': '学院/系别',
        'major_grade': '专业与年级',
        'phone': '联系电话',
        'email': '电子邮箱',
        'student_id': '学号',
        'role': '项目角色',
        'tech_stack': '技术栈/擅长领域',
        'createdAt': '创建时间',
        'updatedAt': '更新时间'
    }


# 创建Admin实例的函数
def setup_admin(app):
    """
    设置Flask-Admin
    """
    # 创建Admin实例，使用自定义的首页视图，设置不同的URL前缀
    admin = Admin(app, name='校园挑战赛管理系统',
                 index_view=MyAdminIndexView(url='/admin/'),
                 template_mode='bootstrap3',
                 url='/admin')
    
    # 添加模型视图
    admin.add_view(TeamView(Team, db.session, name='团队管理', url='/admin/team'))
    admin.add_view(TeamMemberView(TeamMember, db.session, name='成员管理', url='/admin/member'))
    
    return admin