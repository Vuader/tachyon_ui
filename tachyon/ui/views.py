# Tachyon OSS Framework
#
# Copyright (c) 2016-2017, see Authors.txt
# All rights reserved.
#
# LICENSE: (BSD3-Clause)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENTSHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import traceback
import json
from collections import OrderedDict

import tachyon.ui
from tachyon.common import RestClient


import nfw

from tachyon.ui import model


log = logging.getLogger(__name__)


def datatable(req, table_id, url,
              fields, width='100%', view_button=False,
              service=False):
    dom = nfw.web.Dom() 
    table = dom.create_element('table')
    table.set_attribute('id', table_id)
    table.set_attribute('class', 'display')
    table.set_attribute('style', "style=\"width:%s\"" % (width,))

    thead = table.create_element('thead')
    tr = thead.create_element('tr')
    api_fields = []
    for field in fields:
        th = tr.create_element('th')
        th.append(fields[field])
        api_fields.append("%s=%s" % (field, fields[field]))
    if view_button is True:
        th = tr.create_element('th')
        th.append('&nbsp;')
        api_fields.append("%s=%s" % ('id', 'id'))
    id_field_no = len(api_fields) - 1
    api_fields = ",".join(api_fields)

    tfoot = table.create_element('tfoot')
    tr = tfoot.create_element('tr')
    for field in fields:
        th = tr.create_element('th')
        th.append(fields[field])
    if view_button is True:
        th = tr.create_element('th')
        th.append('&nbsp;')

    js = "$(document).ready(function() {"
    js += "var table = $('#%s').DataTable( {" % (table_id,)
    js += "'processing': true,"
    js += "'serverSide': true,"
    js += "'ajax': '%s/dt/?api=%s&fields=%s'" % (req.app, url, api_fields)
    if view_button is True:
        js += ",\"columnDefs\": ["
        js += "{\"targets\": -1,"
        js += "\"data\": null,"
        js += "\"width\": \"26px\","
        js += "\"orderable\": false,"
        js += "\"defaultContent\":"
        js += " '<button class=\"view_button\"></button>'"
        js += "}"
        js += "]"
    js += "} );"
    if view_button is True:
        url = req.get_url()
	js += "$('#%s tbody')" % (table_id,)
        js += ".on( 'click', 'button', function () {"
	js += "var data = table.row( $(this).parents('tr') ).data();"
        if service is False:
            js += "ajax_query(\"#window_content\", \"%s/view/\"+data[%s]);" % (url,
                                                                          id_field_no)
        else:
            js += "ajax_query(\"#service\", \"%s/view/\"+data[%s]);" % (url,
                                                                   id_field_no )
	js += "} );"

    js += "} );"
    script = dom.create_element('script')
    script.append(js)

    return dom.get()


class Globals(nfw.Middleware):
    def __init__(self, app):
        self.config = app.config
        self.ui_config = app.config.get('ui')
        self.app_config = self.config.get('application')
        nfw.jinja.globals['TITLE'] = self.app_config.get('name','Tachyon')  

    def pre(self, req, resp):
        req.context['restapi'] = self.ui_config.get('restapi', '')
        nfw.jinja.globals['NAME'] = self.app_config.get('name')


class Menu():
    def __init__(self):
        self.items = []

    def add(self, item, link, view):
        self.items.append([item, link, view])

    def render(self, app, policy, service=False):
        subs = {}
        menu = nfw.bootstrap3.Menu()
        for item in self.items:
            sub = menu
            item, link, view = item
            if policy.validate(view):
                item = item.strip('/').split('/')
                for (i, l) in enumerate(item):
                    if len(item)-1 == i:
                        if service is True:
                            onclick = "return service(this);"
                            sub.add_link(l, "%s%s" % (app, link),
                                         onclick=onclick)
                        else:
                            onclick = "return admin(this);"
                            sub.add_link(l, "%s%s" % (app, link),
                                         onclick=onclick)
                    else:
                        if l in subs:
                            sub = subs[l]
                        else:
                            s = nfw.bootstrap3.Menu()
                            subs[l] = s
                            if i == 0:
                                sub.add_dropdown(l, s)
                            else:
                                sub.add_submenu(l, s)
                            sub = s
        return menu


def authenticated(req, auth):
    if req.session.get('token') is not None:
        nfw.jinja.globals['LOGIN'] = True
        req.context['roles'] = []
        req.context['domain_admin'] = False
        req.context['domains'] = []
	nfw.jinja.globals['USERNAME'] = auth['username']
        req.session['token'] = req.session['token']
        req.session['domain'] = req.session['domain']
        if 'tenant' in req.session:
            req.session['tenant'] = req.session['tenant']

        for r in auth['roles']:
            if r['domain_name'] not in req.context['domains']:
                req.context['domains'].append(r['domain_name'])
            req.context['roles'].append(r['role_name'])
            if r['domain_name'] == req.session.get('domain'):
                if r['tenant_id'] is None:
                    req.context['domain_admin'] = True
        req.context['login'] = True
    else:
        clear_session(req)


def clear_session(req):
    if 'token' in req.session:
        del req.session['token']
    if 'domain' in req.session:
        del req.session['domain']
    if 'tenant' in req.session:
        del req.session['tenant']
    req.context['login'] = False
    req.context['domain_admin'] = False
    req.context['domains'] = []
    req.context['roles'] = []
    nfw.jinja.globals['LOGIN'] = False


def render_menus(req):
    nfw.jinja.globals['MENU'] = req.app_context['menu'].render(req.app,
                                                               req.policy,
                                                               False)
    nfw.jinja.globals['MENU_ACCOUNTS'] = req.app_context['menu_accounts'].render(req.app,
                                                                                 req.policy,
                                                                                 True)
    nfw.jinja.globals['MENU_SERVICES'] = req.app_context['menu_services'].render(req.app,
                                                                                 req.policy,
                                                                                 True)

class Auth(nfw.Middleware):
    def __init__(self, app):
        pass

    def pre(self, req, resp):
        req.context['login'] = False
        req.context['domain_admin'] = False
        req.context['roles'] = []
        req.context['domains'] = []
        nfw.jinja.globals['LOGIN'] = False

        token = req.session.get('token')
        restapi = req.context['restapi']
        if token is not None:
            api = RestClient(restapi)
            if req.post.get('domain', None) is not None:
                domain = req.post.get('domain', None)
                req.session['domain'] = domain
            else:
                domain = req.session.get('domain')
            if req.post.get('tenant', None) is not None:
                tenant = req.post.get('tenant', None)
                req.session['tenant'] = tenant
            else:
                tenant = req.session.get('tenant')
            auth = {}
            try:
                auth = api.token(token, domain, tenant)
                authenticated(req, auth)
            except tachyon.ui.exceptions.Authentication:
                clear_session(req)

        nfw.jinja.globals['DOMAINS'] = req.context['domains']
        render_menus(req)


class Customers(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/customers', self.view, 'tachyon:public')
        app.router.add(nfw.HTTP_GET, '/customers/view', self.view, 'CUSTOMERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/customers/view/{customer_id}', self.view, 'CUSTOMERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/customers/add', self.add, 'CUSTOMERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/customers/add', self.add, 'CUSTOMERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/customers/edit/{customer_id}', self.edit, 'CUSTOMERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/customers/edit/{customer_id}', self.edit, 'CUSTOMERS:ADMIN')

    def view(self, req, resp, customer_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        pass

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def edit(self, req, resp, customer_id):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()


class User(nfw.Resource):
    def __init__(self, app):
        # VIEW USERS
        app.router.add(nfw.HTTP_GET,
                       '/users',
                       self.view,
                       'users:view')
        app.router.add(nfw.HTTP_GET,
                       '/users/view/{user_id}',
                       self.view,
                       'users:view')
        # ADD NEW USERS
        app.router.add(nfw.HTTP_GET,
                       '/users/create',
                       self.create,
                       'users:admin')
        app.router.add(nfw.HTTP_POST,
                       '/users/create',
                       self.create,
                       'users:admin')
        # EDIT USERS
        app.router.add(nfw.HTTP_GET,
                       '/users/edit/{user_id}', self.edit,
                       'users:admin')
        app.router.add(nfw.HTTP_POST,
                       '/users/edit/{user_id}', self.edit,
                       'users:admin')


    def view(self, req, resp, user_id=None):
        if user_id is None:
            t = nfw.jinja.get_template('tachyon.ui/users/users.html')
            fields = OrderedDict()
            fields['username'] = 'Username'
            fields['email'] = 'Email'

            dt = datatable(req, 'users', '/users',
                           fields, view_button=True, service=False)

            resp.body = t.render(dt=dt)
        else:
            t = nfw.jinja.get_template('tachyon.ui/users/view.html')
            resp.body = t.render(window='#window_content',back='/users')

    def edit(self, req, resp, user_id=None):
	#api = RestClient(req.context['restapi'])
	#headers, response = api.execute(nfw.HTTP_GET,'/users/C0418B28-CCAE-459E-8882-568F433C46FB')
	#userform = model.User(req)
	#userform.load(response)
        t = nfw.jinja.get_template('tachyon.ui/users/edit.html')
        resp.body = t.render()


    def create(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/users/create.html')
        resp.body = t.render()

class Roles(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/users/roles', self.view, 'users:admin')
        app.router.add(nfw.HTTP_GET, '/users/roles/view', self.view, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/view/{role_id}', self.view, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/roles/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/add', self.add, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/roles/add', self.add, 'USERS:ADMIN')

    def view(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/roles/roles.html')
        resp.body = t.render()

    def edit(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

class Domains(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/users/domains', self.view, 'users:admin')
        app.router.add(nfw.HTTP_GET, '/users/domains/view', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/domains/view/{role_id}', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/domains/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/domains/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/domains/add', self.add, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/domains/add', self.add, 'USERS:ADMIN')

    def view(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = "Hello world"

    def edit(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

class Tachyon(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/', self.home, 'tachyon:public')
        app.router.add(nfw.HTTP_GET, '/login', self.login, 'tachyon:public')
        app.router.add(nfw.HTTP_POST, '/login', self.login, 'tachyon:public')
        app.router.add(nfw.HTTP_GET, '/logout', self.logout, 'tachyon:public')
        app.context['menu'] = Menu()
        app.context['menu_accounts'] = Menu()
        app.context['menu_services'] = Menu()
        app.context['menu_accounts'].add('/Account','/customers','tenants:view')
        app.context['menu_accounts'].add('/Billing','/customers','tenants:view')
        app.context['menu_accounts'].add('/Billed','/customers','tenants:view')
        app.context['menu_services'].add('/Bundles','/customers','tenants:view')
        app.context['menu_services'].add('/Email/Accounts','/customers','tenants:view')
        app.context['menu_services'].add('/Email/Aliases','/customers','tenants:view')
        app.context['menu'].add('/Accounts/Customers','/customers','tenants:view')
        app.context['menu'].add('/Accounts/Users','/users','users:view')
        app.context['menu'].add('/Accounts/Roles','/users/roles','users:admin')
        app.context['menu'].add('/Accounts/Domains','/users/domains','users:admin')

    def logout(self, req, resp):
        clear_session(req)
        render_menus(req)
        nfw.view('/login', nfw.HTTP_POST, req, resp)

    def home(self, req, resp):
        if req.session.get('token') is not None:
            t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
            resp.body = t.render()
        else:
            nfw.view('/login', nfw.HTTP_POST, req, resp)

    def login(self, req, resp):
        username = req.post.get('username', '')
        password = req.post.get('password', '')
        domain = req.post.get('domain', 'default')
        restapi = req.context['restapi']
        error = []
        if username != '':
            api = RestClient(restapi)
            try:
                auth = api.authenticate(username, password, domain)
                token = auth['token']
                req.session['token'] = token
                req.session['domain'] = domain
                authenticated(req, auth)
                nfw.jinja.globals['DOMAINS'] = req.context['domains']
                render_menus(req)
            except tachyon.ui.exceptions.Authentication as e:
                clear_session(req)
                error.append(e)

        if req.session.get('token') is not None:
            nfw.view('/', nfw.HTTP_GET, req, resp)
        else:
            t = nfw.jinja.get_template('tachyon.ui/login.html')
            resp.body = t.render(username=username,
                                 password=password,
                                 domain=domain,
                                 error=error)


class DataTables(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/dt', self.dt, 'tachyon:public')
        app.router.add(nfw.HTTP_POST, '/dt', self.dt, 'tachyon:public')

    def dt(self, req, resp):
        url = req.query.get('api', [ '' ])
        api_fields = req.query.get('fields', [ '' ])
        api_fields = api_fields[0].split(",")
        draw = req.query.get('draw', [ 0 ])
        start = req.query.get('start', [ 0 ])
        length = req.query.get('length', [ 0 ])
        search = req.query.get('search[value]', [ None ])
        order = req.query.get("order[0][dir]")
        column = req.query.get("order[0][column]")
        count = 0
        orderby = None
        if order is not None and column is not None:
            order = order[0]
            column = column[0]
            for api_field in api_fields:
                if column == str(count):
                    order_field, order_field_name = api_field.split('=')
                    orderby = "%s %s" % (order_field, order)
                count += 1
        api = RestClient(req.context['restapi'])
        request_headers = {}
        request_headers['X-Pager-Start'] = start[0]
        request_headers['X-Pager-Limit'] = length[0]
        if orderby is not None:
            request_headers['X-Order-By'] = orderby

        if search[0] is not None:
            request_headers['X-Search'] = search[0]
        response_headers, result = api.execute(nfw.HTTP_GET, url[0],
                                               headers=request_headers)


        recordsTotal = int(response_headers.get('X-Total-Rows',0))
        recordsFiltered = int(response_headers.get('X-Filtered-Rows',0))
        response = {}
        response['draw'] = int(draw[0])
        response['recordsTotal'] = recordsTotal
        response['recordsFiltered'] = recordsFiltered
        data = []
        for row in result:
            fields = []
            for api_field in api_fields:
                field, name = api_field.split("=")
                fields.append(row[field])
            data.append(fields)
        response['data'] = data
        return json.dumps(response, indent=4)
