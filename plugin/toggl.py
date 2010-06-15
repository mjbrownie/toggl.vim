from __future__ import with_statement
import simplejson, urllib
import os
import urllib
import urllib2, base64
from glob import glob

URL = 'https://www.toggl.com/api/v1/'

PROJECT_PATHS = ['/home/michael/django_apps/*'] #TODO this needs to be set in vim!

RENDER_TASKS ="""
Task:

    billable: %s
    description: %s
    duration: %s
    id: %s
    start: '%s'
    stop: '%s'
    tag_names: %s
    workspace':
        id: %s
        name: %s
"""

RENDER_PROJECTS = """

name: %s,
 billable %s
 workspace:
    name: %s
fixed fee: %s
hourly rate: %s
is fixed fee: %s
client project name: %s
estimated workhours: %s
"""

class Toggl:
    

    project_paths = PROJECT_PATHS #TODO make a vim var
    def __init__(self, token):
        self.token = token

        self.current_task = {'description': "Worked on %s" % (os.getcwd())}

    def render_tasks(self):
        self.get_tasks()

        render = ''

        for task in self.tasks:
            render +=  RENDER_TASKS % ( task['billable'],
                        task['description'],
                        task['duration'],
                        task['id'],
                        task['start'],
                        task['stop'],
                        task['tag_names'],
                        task['workspace']['id'],
                        task['workspace']['name'])

        print render

    def get_tasks(self):
        self.tasks = self._json_request('tasks.json')

    def get_projects(self):
        self.projects = self._json_request('projects.json')

    def get_workspaces(self):
        self.workspaces = self._json_request('workspaces.json')

    def load_project(self):
        with open(".toggl.%s.json" %(os.getlogin(),), 'r') as fp:
            self.current_project=simplejson.load(fp)
            fp.close()

    def save_project(self):
        with open(".toggl.%s.json" %(os.getlogin(),), 'w') as fp:
            simplejson.dump(self.current_project,fp)
            fp.close()

    def set_current_project(self,name):
        for project in self.projects:
            if project['name'] == name:
                self.current_project = project

    def create_project(self,name,billable=True,workspace=None):
        if not workspace:
            self.get_workspaces()
            workspace = self.workspaces[0]['id']

        self.current_project = self._json_request('projects.json',{'project':{
            'billable':billable, 'workspace':{'id':workspace},'name':name }})

        self.save_project()

    def auto_project(self):
        """ This will auto create a project based upon a file path """
        for path in self.project_paths:
            if os.getcwd() in glob(path):
                self.create_project(os.getcwd())
                return True

        return False

    def send_task(self, start_time, stop_time):

        import datetime

        try:
            self.load_project()
        except:
            if not self.auto_project():
                return

        self._json_request('tasks.json', {
        "task":{
            "tag_names"    :["toggl.vim"],
            "billable"     : True,
            "workspace"    : {"id": self.current_project['workspace']['id']},
            "description"  : self.current_task['description'],
            "start"        : start_time,
            "stop"         : stop_time,
            "duration"     : (datetime.datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S") \
                               - datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")).seconds,
            "created_with" : "toggl.vim"}
        })

    def _json_request(self, url, parameters=None):
        """ urllib wrapper adding authentication """

        url = URL + url

        username = self.token
        password = 'api_token'

        if parameters:
            parameters = simplejson.JSONEncoder().encode(parameters)

        request = urllib2.Request(url, parameters)

        if parameters:
            request.add_header("Content-type", "application/json")

        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        res = urllib2.urlopen(request)
        result = simplejson.load(res)

        return result
