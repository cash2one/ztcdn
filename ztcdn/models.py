# -*- coding: utf-8 -*-
__author__ = 'liujiahua'
from ztcdn import db

# 域名表
class cdn_manage_domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(80))
    domain_type = db.Column(db.String(120))
    domain_status = db.Column(db.String(120))
    domain_id = db.Column(db.String(120))
    ip_list = db.Column(db.String(120))
    project_id = db.Column(db.String(120))
    user_name = db.Column(db.String(120))
    test_url = db.Column(db.String(120))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    def __init__(self, domain_name=domain_name, domain_type=domain_type, domain_status=domain_status,
                 domain_id=domain_id, ip_list=ip_list, project_id=project_id, user_name=user_name,
                 test_url=test_url, create_time=create_time, update_time=update_time):
        self.domain_name = domain_name
        self.domain_type = domain_type
        self.domain_status = domain_status
        self.domain_id = domain_id
        self.ip_list = ip_list
        self.project_id = project_id
        self.user_name = user_name
        self.test_url = test_url
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Domain %r>' % self.domain_name

# 厂商域名表
class cdn_manage_sp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(80))
    domain_cname = db.Column(db.String(80))
    sp_domain_type = db.Column(db.String(80))
    sp_domain_status = db.Column(db.String(80))
    sp_domain_id = db.Column(db.String(80))
    sp_etag = db.Column(db.String(80))
    domain_table_id = db.Column(db.Integer, db.ForeignKey('cdn_manage_domain.id'))

    def __init__(self, domain_name=domain_name, domain_cname=domain_cname, sp_domain_type=sp_domain_type,
                 sp_domain_status=sp_domain_status, sp_domain_id=sp_domain_id, sp_etag=sp_etag,
                 domain_table_id=domain_table_id):
        self.domain_name = domain_name
        self.domain_cname = domain_cname
        self.sp_domain_type = sp_domain_type
        self.sp_domain_status = sp_domain_status
        self.sp_domain_id = sp_domain_id
        self.sp_etag = sp_etag
        self.domain_table_id = domain_table_id

    def __repr__(self):
        return '<DomainCname %r>' % self.domain_cname

# 缓存策略表
class cdn_manage_cacherules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cache_path = db.Column(db.String(80))
    cache_time = db.Column(db.String(80))
    ignore_param_req = db.Column(db.String(20))
    domain_table_id = db.Column(db.Integer, db.ForeignKey('cdn_manage_domain.id'))

    def __init__(self, cache_path=cache_path, cache_time=cache_time, ignore_param_req=ignore_param_req,
                 domain_table_id=domain_table_id):
        self.cache_path = cache_path
        self.cache_time = cache_time
        self.ignore_param_req = ignore_param_req
        self.domain_table_id = domain_table_id

    def __repr__(self):
        return '<DomainCache %r>' % self.cache_path

# 刷新缓存、预缓存任务主表
class cdn_manage_tasklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(80))
    project_id = db.Column(db.String(80))
    task_type = db.Column(db.String(80))
    task_content = db.Column(db.String(80))
    task_status = db.Column(db.String(80))
    task_user = db.Column(db.String(80))
    task_create_at = db.Column(db.DateTime)
    task_done_at = db.Column(db.DateTime)

    def __init__(self, task_id=task_id, project_id=project_id, task_type=task_type, task_content=task_content,
                 task_status=task_status, task_user=task_user, task_create_at=task_create_at,
                 task_done_at=task_done_at):
        self.task_id = task_id
        self.project_id = project_id
        self.task_type = task_type
        self.task_content = task_content
        self.task_status = task_status
        self.task_user = task_user
        self.task_create_at = task_create_at
        self.task_done_at = task_done_at

    def __repr__(self):
        return '<Task %r>' % self.task_content

# 刷新缓存、预缓存厂商任务表
class cdn_manage_sp_tasklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sp_task_id = db.Column(db.String(80))
    sp_task_type = db.Column(db.String(80))
    sp_task_status = db.Column(db.String(80))
    sp_domain_type = db.Column(db.String(80))
    task_done_at = db.Column(db.DateTime)
    task_table_id = db.Column(db.Integer, db.ForeignKey('cdn_manage_tasklist.id'))

    def __init__(self, sp_task_id=sp_task_id, sp_task_type=sp_task_type, sp_task_status=sp_task_status,
                 sp_domain_type=sp_domain_type, task_done_at=task_done_at, task_table_id=task_table_id):
        self.sp_task_id = sp_task_id
        self.sp_task_type = sp_task_type
        self.sp_task_status = sp_task_status
        self.sp_domain_type = sp_domain_type
        self.task_done_at = task_done_at
        self.task_table_id = task_table_id

    def __repr__(self):
        return '<TaskSP %r>' % self.sp_task_id

# 根据service类型使用厂商表
class cdn_manage_sp_choose(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(20))
    used_sp_list = db.Column(db.String(80))

    def __init__(self, service_type=service_type, used_sp_list=used_sp_list):
        self.service_type = service_type
        self.used_sp_list = used_sp_list

    def __repr__(self):
        return '<TaskSP %r>' % self.used_sp_list
