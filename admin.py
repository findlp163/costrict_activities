"""
Flask-Admin配置文件
定义管理界面的模型视图和自定义行为
"""

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from flask import redirect, url_for, request, abort, Response
import os
from models import db, Team, TeamMember, Config


class AuthMixin:
    """
    认证混入类，用于统一管理Flask-Admin视图的认证逻辑
    """
    def is_accessible(self):
        # 简单的HTTP基本认证
        auth = request.authorization
        if not auth or not self.check_auth(auth.username, auth.password):
            return False
        return True
    
    def check_auth(self, username, password):
        # 从环境变量获取用户名和密码，如果环境变量不存在则使用默认值
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
        return username == admin_username and password == admin_password
    
    def inaccessible_callback(self, name, **kwargs):
        # 返回401未授权响应，触发浏览器显示基本认证对话框
        return Response(
            '请提供有效的管理员凭据',
            401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )


class MyAdminIndexView(AuthMixin, AdminIndexView):
    """
    自定义管理界面首页视图，添加基本认证
    """
    
    @expose('/')
    def index(self):
        # 这里可以添加自定义的首页逻辑
        return super(MyAdminIndexView, self).index()
    
    @expose('/logout')
    def logout(self):
        # 简单重定向到首页
        return redirect('/')


class TeamView(AuthMixin, ModelView):
    """
    团队模型的管理视图 - 简化配置，显示所有字段
    """
    # 启用列表页面的详情查看功能
    can_view_details = True
    
    # 启用导出功能
    can_export = True
    export_max_rows = 0  # 0=不限制，默认 1000
    
    # 每页显示的记录数
    page_size = 20
    
    def on_model_change(self, form, model, is_created):
        """在模型保存前调用，自动更新时间戳"""
        if not is_created:
            # 更新现有记录时，手动更新时间戳
            model.update_timestamps()
        return super(TeamView, self).on_model_change(form, model, is_created)
    
    # 指定列表页面显示的字段
    column_list = ('id', 'createdAt', 'updatedAt', 'team_name', 'competition_track',
                  'project_name', 'repo_url', 'costrict_uid')
    
    # 指定导出时包含的字段（所有字段）
    column_export_list = ('id', 'createdAt', 'updatedAt', 'team_name', 'competition_track',
                   'project_name', 'repo_url', 'costrict_uid', 'project_intro',
                   'tech_solution', 'goals_and_outlook')
    
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


class TeamMemberView(AuthMixin, ModelView):
    """
    团队成员模型的管理视图 - 简化配置，显示所有字段
    """
    # 启用列表页面的详情查看功能
    can_view_details = True
    
    # 启用导出功能
    can_export = True
    export_max_rows = 0  # 0=不限制，默认 1000
    
    # 每页显示的记录数
    page_size = 20
    
    def on_model_change(self, form, model, is_created):
        """在模型保存前调用，自动更新时间戳"""
        if not is_created:
            # 更新现有记录时，手动更新时间戳
            model.update_timestamps()
        return super(TeamMemberView, self).on_model_change(form, model, is_created)
    
    # 指定列表页面显示的字段
    column_list = ('id', 'team_id', 'team_name', 'name', 'member_type', 'school',
                  'department', 'major_grade', 'phone', 'email', 'student_id',
                  'role', 'tech_stack', 'createdAt', 'updatedAt')
    
    # 指定导出时包含的字段（所有字段）
    column_export_list = ('id', 'team_id', 'team_name', 'name', 'member_type', 'school',
                    'department', 'major_grade', 'phone', 'email', 'student_id',
                    'role', 'tech_stack', 'desc', 'createdAt', 'updatedAt')
    
    # 指定表单中显示的字段
    form_columns = ('team_id', 'team_name', 'name', 'member_type', 'school',
                   'department', 'major_grade', 'phone', 'email', 'student_id',
                   'role', 'tech_stack', 'desc')
    
    # 指定详情页面显示的字段
    column_details_list = ('id', 'team_id', 'team_name', 'name', 'member_type', 'school',
                          'department', 'major_grade', 'phone', 'email', 'student_id',
                          'role', 'tech_stack', 'desc', 'createdAt', 'updatedAt')
    
    # 定义搜索字段
    column_searchable_list = ('name', 'school', 'phone', 'email', 'team_name', 'tech_stack')
    
    # 定义过滤器
    column_filters = ('member_type', 'school', 'phone', 'email', 'team_name', 'tech_stack')
    
    # 自定义显示名称 - 中文字段标题
    column_labels = {
        'id': 'ID',
        'team_id': '团队ID',
        'team_name': '团队名称',
        'name': '姓名',
        'member_type': '成员类型',
        'school': '学校/单位',
        'department': '学院/系别',
        'major_grade': '专业与年级',
        'phone': '联系电话',
        'email': '电子邮箱',
        'student_id': '学号',
        'role': '项目角色',
        'tech_stack': '技术栈/擅长领域',
        'desc': '个人简介/备注',
        'createdAt': '创建时间',
        'updatedAt': '更新时间'
    }
    
    # 为成员类型提供选择器
    form_choices = {
        'member_type': [
            ('队员', '队员'),
            ('队长', '队长'),
            ('指导老师', '指导老师')
        ]
    }


class ConfigView(AuthMixin, ModelView):
    """
    配置模型的管理视图 - 用于管理系统配置
    """
    # 启用列表页面的详情查看功能
    can_view_details = True
    
    # 禁用导出功能
    can_export = False
    
    # 每页显示的记录数
    page_size = 20
    
    def on_model_change(self, form, model, is_created):
        """在模型保存前调用，自动更新时间戳"""
        if not is_created:
            # 更新现有记录时，手动更新时间戳
            model.update_timestamps()
        return super(ConfigView, self).on_model_change(form, model, is_created)
    
    # 指定列表页面显示的字段
    column_list = ('id', 'config_key', 'config_value', 'config_type', 'description', 'createdAt', 'updatedAt')
    
    # 指定表单中显示的字段
    form_columns = ('config_key', 'config_value', 'config_type', 'description')
    
    # 指定详情页面显示的字段
    column_details_list = ('id', 'config_key', 'config_value', 'config_type', 'description', 'createdAt', 'updatedAt')
    
    # 定义搜索字段
    column_searchable_list = ('config_key', 'config_value', 'description')
    
    # 定义过滤器
    column_filters = ('config_key', 'config_type', 'createdAt', 'updatedAt')
    
    # 自定义显示名称 - 中文字段标题
    column_labels = {
        'id': 'ID',
        'config_key': '配置键',
        'config_value': '配置值',
        'config_type': '配置类型',
        'description': '描述',
        'createdAt': '创建时间',
        'updatedAt': '更新时间'
    }
    
    # 为配置类型提供选择器
    form_choices = {
        'config_type': [
            ('str', '字符串'),
            ('int', '整数'),
            ('datetime', '日期时间')
        ]
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
    admin.add_view(ConfigView(Config, db.session, name='系统配置', url='/admin/config'))
    
    # 添加自定义模板目录，这样我们可以覆盖默认模板
    admin.add_link(MenuLink(name='退出登录', url='/admin/logout', category=None))
    
    return admin


