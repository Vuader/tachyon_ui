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
import json
from collections import OrderedDict
from StringIO import StringIO
import time

import nfw

import tachyon.ui
import tachyon.common
from tachyon.common import RestClient
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
        nfw.jinja.globals['NAME'] = self.app_config.get('name')

    def pre(self, req, resp):
        nfw.jinja.globals['REQUEST_ID'] = req.request_id
        nfw.jinja.globals[''] = self.app_config.get('name','Tachyon')  
        req.context['restapi'] = self.ui_config.get('restapi', '')
        resp.headers['Content-Type'] = nfw.TEXT_HTML


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
        if 'token' in req.session:
            req.session['token'] = req.session['token']
        if 'domain' in req.session:
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
        # DELETE USERS
        app.router.add(nfw.HTTP_GET,
                       '/users/delete/{user_id}', self.delete,
                       'users:admin')
        app.router.add(nfw.HTTP_POST,
                       '/users/delete/{user_id}', self.delete,
                       'users:admin')


    def view(self, req, resp, user_id=None):
        raise nfw.HTTPBadRequest('page not found for you',' yes man')
        renderValues = {}
        renderValues['resource'] = 'User'
        renderValues['window'] = '#window_content'
        if user_id is None:
            t = nfw.jinja.get_template('tachyon.ui/users/users.html')
            fields = OrderedDict()
            fields['username'] = 'Username'
            fields['email'] = 'Email'

            dt = datatable(req, 'users', '/users',
                           fields, view_button=True, service=False)

            renderValues['dt'] = dt
            renderValues['create_url'] = 'users/create'
            resp.body = t.render(**renderValues)
        else:
            renderValues['back_url'] = 'users'
            renderValues['edit_url'] = 'users/edit/' + user_id
            # We should fetch the Username from db for the title
            # For now just setting to static
	    renderValues['title'] = 'View User'
            t = nfw.jinja.get_template('tachyon.ui/users/view.html')
            resp.body = t.render(**renderValues)


    def edit(self, req, resp, user_id=None):
        renderValues = {}
        renderValues['title'] = 'Edit User'
        renderValues['back_url'] = 'users/view/' + user_id
        renderValues['window'] = '#window_content'
        renderValues['submit_url'] = 'users/edit/' + user_id
        renderValues['delete_url'] = 'users/delete/' + user_id
        renderValues['formid'] = 'user'
        renderValues['resource'] = 'User'
	api = RestClient(req.context['restapi'])
	headers, response = api.execute(nfw.HTTP_GET,'/users/' + user_id)
	userform = model.User(req)
	userform.load(response)
        t = nfw.jinja.get_template('tachyon.ui/users/edit.html')
        resp.body = t.render(**renderValues)


    def create(self, req, resp):
        renderValues = {}
        renderValues['title'] = 'Create User'
        renderValues['back_url'] = 'users'
        renderValues['window'] = '#window_content'
        renderValues['submit_url'] = 'users/create'
        renderValues['formid'] = 'user'
        renderValues['resource'] = 'User'	
        t = nfw.jinja.get_template('tachyon.ui/users/create.html')
        resp.body = t.render(**renderValues)


    def delete(self, req, resp, user_id=None):
        renderValues = {}
        renderValues['title'] = 'Delete User'
        renderValues['back_url'] = 'users/edit/' + user_id
        renderValues['window'] = '#window_content'
        renderValues['delete_url'] = 'users/delete/' + user_id
        renderValues['formid'] = 'user'
        renderValues['resource'] = 'User'
        t = nfw.jinja.get_template('tachyon.ui/users/delete.html')
        resp.body = t.render(**renderValues)

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
            except nfw.RestClientError as e:
                clear_session(req)
                error.append(e)

        if req.session.get('token') is not None:
            # resp.view('/', nfw.HTTP_GET)
            resp.redirect('/')
        else:
            t = nfw.jinja.get_template('tachyon.ui/login.html')
            resp.body = t.render(username=username,
                                 password=password,
                                 domain=domain,
                                 error=error)


class Messaging(nfw.Resource): 
    def __init__(self, app): 
        app.router.add(nfw.HTTP_GET, '/messaging', self.get, 'tachyon:public')

    class Server(object):
        def __init__(self, req, resp):
            self.req = req
            self.resp = resp
            self.login = True
            self.sent = False
            self.timer = nfw.timer()

        def read(self, size=0):
            messages = []
            if self.req.context['login'] is False:
                messages.append({'type': 'goto',
                                 'link': self.req.get_app_url()+'logout' })

            while True:
                time.sleep(1)
                if nfw.timer(self.timer) > 50:
                    reset = True
                    self.timer = nfw.timer()
                else:
                    reset = False

                if self.sent is True or reset is True:
                    return None
                else:
                    if len(messages) > 0:
                        self.sent = True
                        return json.dumps(messages, indent=4)

    def get(self, req, resp):
        server = self.Server(req, resp)
        return nfw.response.ResponseIoStream(server)
                


class DataTables(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/dt', self.dt, 'tachyon:public')
        app.router.add(nfw.HTTP_POST, '/dt', self.dt, 'tachyon:public')

    def dt(self, req, resp):
        resp.headers['Content-Type'] = nfw.APPLICATION_JSON 
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


class Themes(nfw.Resource):
    def __init__(self, app):
        app_config = app.config.get('application') 
        static = app_config.get('static', '').rstrip('/')
        images = "%s/tachyon.ui/images" % (static,)
        self.css = OrderedDict()
        self.css['body'] = {}
        self.css['body']['background'] = '#E7E8EB'
        self.css['body']['margin-bottom'] = '0px'
        self.css['body']['margin-left'] = '0px'
        self.css['body']['margin-right'] = '0px'
        self.css['body']['margin-top'] = '0px'
        self.css['.modal-dialog'] = {}
        self.css['.modal-dialog']['width'] = '75%'
        self.css['button.view_button'] = {}
        view_button = self.css['button.view_button']
        view_button['height'] = '24px'
        view_button['width'] = '24px'
        view_button['border'] = '0px'
        view_button['background-color'] = '#FFFFFF'
        view_button['background-image'] = "url(\"%s/view.png\")" % (images,)
        self.css['button.edit_button'] = {}
        edit_button = self.css['button.edit_button']
        edit_button['height'] = '24px'
        edit_button['width'] = '24px'
        edit_button['border'] = '0px'
        edit_button['background-color'] = '#FFFFFF'
        edit_button['background-image'] = "url(\"%s/edit.png\")" % (images,)
        self.css['div.locked'] = {}
        self.css['div.locked']['display'] = 'none'
        self.css['div.locked']['background-color'] = '#000000'
        self.css['div.locked']['overflow'] = 'hidden'
        self.css['div.locked']['position'] = 'fixed'
        self.css['div.locked']['z-index'] = '1003'
        self.css['div.locked']['top'] = '0'
        self.css['div.locked']['left'] = '0'
        self.css['div.locked']['height'] = '100%'
        self.css['div.locked']['width'] = '100%'
        self.css['div.locked']['opacity'] = '0.6'
        self.css['div.window'] = {}
        self.css['div.window']['display'] = 'none'
        self.css['div.window']['position'] = 'absolute'
        self.css['div.window']['top'] = '50px'
        self.css['div.window']['left'] = '10%'
        self.css['div.window']['right'] = '10%'
        self.css['div.window']['margin'] = 'auto'
        self.css['div.window']['width'] = '80%'
        self.css['div.window']['height'] = 'auto'
        self.css['div.window']['background-color'] = '#FFFFFF'
        self.css['div.window']['z-index'] = '1004'
        self.css['div.window']['overflow'] = 'auto'
        self.css['div.window']['border'] = '1px solid rgba(0, 0, 0, .2)'
        self.css['div.window']['border-radius'] = '6px'
        self.css['div.window']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['div.loading'] = {}
        self.css['div.loading']['display'] = 'none'
        self.css['div.loading']['overflow'] = 'hidden'
        self.css['div.loading']['position'] = 'fixed'
        self.css['div.loading']['z-index'] = '5000'
        self.css['div.loading']['top'] = '0'
        self.css['div.loading']['left'] = '0'
        self.css['div.loading']['height'] = '100%'
        self.css['div.loading']['width'] = '100%'
        self.css['div.loading']['background'] = 'rgba( 255, 255, 255, .5 )'
        self.css['div.loading']['background'] += "url(\'%s" % (images,)
        self.css['div.loading']['background'] += '/loader.gif\')'
        self.css['div.loading']['background'] += '50% 50% no-repeat'
        self.css['@media (min-width: 1350px)'] = {}
        self.css['@media (min-width: 1350px)']['.container'] = {}
        self.css['@media (min-width: 1350px)']['.container']['width'] = '1300px'
        self.css['@media (max-width: 800px)'] = {}
        self.css['@media (max-width: 800px)']['.navbar-header'] = {}
        self.css['@media (max-width: 800px)']['.navbar-header']['float'] = 'none'
        self.css['@media (max-width: 800px)']['.navbar-left,.navbar-right'] = {}
        self.css['@media (max-width: 800px)']['.navbar-left,.navbar-right']['float'] = 'none !important'
        self.css['@media (max-width: 800px)']['.navbar-toggle'] = {}
        self.css['@media (max-width: 800px)']['.navbar-toggle']['display'] = 'block'
        self.css['@media (max-width: 800px)']['.navbar-collapse'] = {}
        self.css['@media (max-width: 800px)']['.navbar-collapse']['border-top'] = '1px solid transparent'
        self.css['@media (max-width: 800px)']['.navbar-collapse']['box-shadow'] = 'inset 0 1px 0 rgba(255,255,255,0.1)'
        self.css['@media (max-width: 800px)']['.navbar-fixed-top'] = {}
        self.css['@media (max-width: 800px)']['.navbar-fixed-top']['top'] = '0'
        self.css['@media (max-width: 800px)']['.navbar-fixed-top']['border-width'] = '0 0 1px'
        self.css['@media (max-width: 800px)']['.navbar-collapse.collapse'] = {}
        self.css['@media (max-width: 800px)']['.navbar-collapse.collapse']['display'] = 'none!important'
        self.css['@media (max-width: 800px)']['.navbar-nav'] = {}
        self.css['@media (max-width: 800px)']['.navbar-nav']['float'] = 'none!important'
        self.css['@media (max-width: 800px)']['.navbar-nav']['margin-top'] = '7.5px'
        self.css['@media (max-width: 800px)']['.navbar-nav>li'] = {}
        self.css['@media (max-width: 800px)']['.navbar-nav>li']['float'] = 'none'
        self.css['@media (max-width: 800px)']['.navbar-nav>li>a'] = {}
        self.css['@media (max-width: 800px)']['.navbar-nav>li>a']['padding-top'] = '10px'
        self.css['@media (max-width: 800px)']['.navbar-nav>li>a']['padding-bottom'] = '10px'
        self.css['@media (max-width: 800px)']['.collapse.in'] = {}
        self.css['@media (max-width: 800px)']['.collapse.in']['display'] = 'block !important'
        self.css['.dropdown-menu'] = {}
        self.css['.dropdown-menu']['border-radius'] = '0px'
        self.css['.dropdown-menu']['-webkit-box-shadow'] = 'none'
        self.css['.dropdown-menu']['box-shadow'] = 'none'
        self.css['.dropdown-submenu'] = {}
        self.css['.dropdown-submenu']['position'] = 'initial'
        self.css['.dropdown-submenu>.dropdown-menu'] = {}
        self.css['.dropdown-submenu>.dropdown-menu']['top'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['left'] = '100%'
        self.css['.dropdown-submenu>.dropdown-menu']['margin-top'] = '-1px'
        self.css['.dropdown-submenu>.dropdown-menu']['margin-left'] = '-1px'
        self.css['.dropdown-submenu>.dropdown-menu']['-webkit-border-radius'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['-moz-border-radius'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['border-radius'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['min-height'] = '101%'
        self.css['.dropdown-submenu:hover>.dropdown-menu'] = {}
        self.css['.dropdown-submenu:hover>.dropdown-menu']['display'] = 'block'
        self.css['.dropdown-submenu>a:after'] = {}
        self.css['.dropdown-submenu>a:after']['display'] = 'block'
        self.css['.dropdown-submenu>a:after']['content'] = '" "'
        self.css['.dropdown-submenu>a:after']['float'] = 'right'
        self.css['.dropdown-submenu>a:after']['width'] = '0'
        self.css['.dropdown-submenu>a:after']['height'] = '0'
        self.css['.dropdown-submenu>a:after']['border-color'] = 'transparent'
        self.css['.dropdown-submenu>a:after']['border-style'] = 'solid'
        self.css['.dropdown-submenu>a:after']['border-width'] = '5px 0 5px 5px'
        self.css['.dropdown-submenu>a:after']['border-left-color'] = '#ccc'
        self.css['.dropdown-submenu>a:after']['margin-top'] = '5px'
        self.css['.dropdown-submenu>a:after']['margin-right'] = '-10px'
        self.css['.dropdown-submenu:hover>a:after'] = {}
        self.css['.dropdown-submenu:hover>a:after']['border-left-color'] = '#fff'
        self.css['.dropdown-submenu.pull-left'] = {}
        self.css['.dropdown-submenu.pull-left']['float'] = 'none'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu'] = {}
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['left'] = '-100%'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['margin-left'] = '10px'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['-webkit-border-radius'] = '6px 0 6px 6px'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['-moz-border-radius'] = '6px 0 6px 6px'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['border-radius'] = '6px 0 6px 6px'
        self.css['#popup'] = {}
        self.css['#popup']['z-index'] = '4000'
        self.css['#popup']['width'] = '300px'
        self.css['#popup']['position'] = 'fixed'
        self.css['#popup']['top'] = '50px'
        self.css['#popup']['left'] = 'auto'
        self.css['#popup']['right'] = '10px'
        self.css['#popup']['font-family'] = 'helvetica,arial,sans-serif'
        self.css['#popup']['font-size'] = '8pt'
        self.css['div.error'] = {}
        self.css['div.error']['background-color'] = '#f4e2e3'
        self.css['div.error']['color'] = '#9a6e6f'
        self.css['div.warning'] = {}
        self.css['div.warning']['background-color'] = '#fff4c3'
        self.css['div.warning']['color'] = '#b09100'
        self.css['div.info'] = {}
        self.css['div.info']['background-color'] = '#deeff7'
        self.css['div.info']['color'] = '#6d8a98'
        self.css['div.success'] = {}
        self.css['div.success']['background-color'] = '#e2f2dd'
        self.css['div.success']['color'] = '#598766'
        self.css['div.popup'] = {}
        self.css['div.popup']['border-color'] = '#D8D8D8'
        self.css['div.popup']['border-style'] = 'solid'
        self.css['div.popup']['border-width'] = '1px'
        self.css['div.popup']['margin-bottom'] = '10px'
        self.css['div.popup']['margin-left'] = '0px'
        self.css['div.popup']['margin-right'] = '0px'
        self.css['div.popup']['margin-top'] = '0px'
        self.css['div.popup']['padding-bottom'] = '5px'
        self.css['div.popup']['padding-left'] = '5px'
        self.css['div.popup']['padding-right'] = '5px'
        self.css['div.popup']['padding-top'] = '5px'
        self.css['div.popup']['width'] = '100%'
        self.css['div.popup']['border-radius'] = '8px'
        self.css['div.popup']['overflow'] = 'hidden'
        self.css['div.signin'] = {}
        self.css['div.signin']['width'] = '50%'
        self.css['div.signin']['max-width'] = '400px'
        self.css['div.signin']['min-width'] = '200px'
        self.css['div.signin']['margin'] = 'auto'
        self.css['div.block'] = {}
        self.css['div.block']['box-shadow'] = '5px 5px 5px #888888'
        self.css['div.block']['opacity'] = '0.9'
        self.css['div.block']['background-color'] = '#FFFFFF'
        self.css['div.block']['border-color'] = '#D8D8D8'
        self.css['div.block']['border-style'] = 'solid'
        self.css['div.block']['border-width'] = '1px'
        self.css['div.block']['color'] = '#5B5B5B'
        self.css['div.block']['font-family'] = 'helvetica,arial,sans-serif'
        self.css['div.block']['font-size'] = '12px'
        self.css['div.block']['margin-bottom'] = '10px'
        self.css['div.block']['margin-left'] = '0px'
        self.css['div.block']['margin-right'] = '0px'
        self.css['div.block']['margin-top'] = '0px'
        self.css['div.block']['padding-bottom'] = '5px'
        self.css['div.block']['padding-left'] = '5px'
        self.css['div.block']['padding-right'] = '5px'
        self.css['div.block']['padding-top'] = '5px'
        self.css['div.block']['width'] = '100%'
        self.css['div.block']['border-radius'] = '8px'
        self.css['div.block_title'] = {}
        self.css['div.block_title']['border-bottom-width'] = '1px'
        self.css['div.block_title']['border-color'] = '#D8D8D8'
        self.css['div.block_title']['border-left-width'] = '0px'
        self.css['div.block_title']['border-right-width'] = '0px'
        self.css['div.block_title']['border-style'] = 'solid'
        self.css['div.block_title']['border-top-width'] = '0px'
        self.css['div.block_title']['color'] = '#318BBB'
        self.css['div.block_title']['font'] = "bold 15px 'lucida sans',"
        self.css['div.block_title']['font'] += "'trebuchet MS', 'Tahoma'"
        self.css['div.block_title']['margin-bottom'] = '5px'
        self.css['div.block_title']['margin-left'] = '0px'
        self.css['div.block_title']['margin-right'] = '0px'
        self.css['div.block_title']['margin-top'] = '0px'
        self.css['div.block_title']['width'] = '100%'
        self.css['div.block_content'] = {}
        self.css['div.block_content']['border-bottom-width'] = '0px'
        self.css['div.block_content']['border-left-width'] = '0px'
        self.css['div.block_content']['border-right-width'] = '0px'
        self.css['div.block_content']['border-top-width'] = '0px'
        self.css['div.block_content']['margin-bottom'] = '5px'
        self.css['div.block_content']['margin-left'] = '0px'
        self.css['div.block_content']['margin-right'] = '0px'
        self.css['div.block_content']['margin-top'] = '0px'
        self.css['div.block_content']['width'] = '100%'
        self.css['div.menu'] = {}
        self.css['div.menu']['z-index'] = '1002'
        self.css['div.menu']['position'] = 'relative'
        self.css['div.menu_accounts'] = {}
        self.css['div.menu_accounts']['z-index'] = '1001'
        self.css['div.menu_accounts']['position'] = 'relative'
        self.css['div.menu_services'] = {}
        self.css['div.menu_services']['z-index'] = '1000'
        self.css['div.menu_services']['position'] = 'relative'
        self.css['div.push_top'] = {}
        self.css['div.push_top']['height'] = '70px'
        self.css['div.push_top']['width'] = '100%'
        self.css['div.push_top']['clear'] = 'both'
        self.css['div.push_top']['z-index'] = '1'
        self.css['div.push_bottom'] = {}
        self.css['div.push_bottom']['height'] = '25px'
        self.css['div.push_bottom']['width'] = '100%'
        self.css['div.push_bottom']['clear'] = 'both'
        self.css['div.push_bottom']['z-index'] = '1'
        self.css['footer'] = {}
        self.css['footer']['background-color'] = '#5B5B5B'
        self.css['footer']['bottom'] = '0px'
        self.css['footer']['clear'] = 'both'
        self.css['footer']['color'] = '#FFFFFF'
        self.css['footer']['font-size'] = '12px'
        self.css['footer']['height'] = '20px'
        self.css['footer']['line-height'] = '20px'
        self.css['footer']['margin-bottom'] = '0px'
        self.css['footer']['margin-top'] = '0px'
        self.css['footer']['position'] = 'fixed'
        self.css['footer']['text-align'] = 'center'
        self.css['footer']['z-index'] = '1010'
        self.css['footer']['width'] = '100%'
        self.css['footer:before'] = {}
        self.css['footer:before']['content'] = '"Tachyon Framework - Copyright (c) 2016 to 2017, Christiaan Frans Rademan, Dave Kruger. All rights resevered. BSD3-Clause License"'
        self.css['footer:after'] = {}
        app.context['css'] = self.css
        app.router.add(nfw.HTTP_GET, '/css', self.get, 'tachyon:public')

    def get(self, req, resp):
        resp.headers['Content-Type'] = nfw.TEXT_CSS

        def css(d, tab=0):
            spacer = "    " * tab
            for v in d:
                if isinstance(d[v], dict):
                    resp.write("%s%s {\n" % (spacer, v,))
                    css(d[v], tab+1)
                    resp.write("%s}\n\n" % (spacer,))
                else:
                    val = "%s;" % (d[v].rstrip(';'),)
                    resp.write("%s%s: %s\n" % (spacer, v, val))

        css(self.css)

