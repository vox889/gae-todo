import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required

class ToDoList(db.Model):
    author = db.UserProperty()
    name = db.StringProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)

class ToDoListItem(db.Model):
    name = db.StringProperty()
    desc = db.StringProperty()
    checked = db.BooleanProperty(default=False)
    list = db.ReferenceProperty(ToDoList, collection_name='items')

# template directory
TEMPLATE_DIR = 'template'

def render_template(name, values):
    path = os.path.join(os.path.dirname(__file__), TEMPLATE_DIR, name)
    return template.render(path, values)

class MainHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.uri)
        todo_lists = db.GqlQuery("SELECT * FROM ToDoList WHERE author = :user ORDER BY created_date DESC",
        						  user=user)
        self.response.out.write(render_template('main.html', {
                                   'user': user,
                                   'logout_url': logout_url,
                                   'todo_lists': todo_lists,
                                   'count': todo_lists.count()
        						}))

    def post(self):
        list_name = self.request.get('name')
        new_list = ToDoList(author=users.get_current_user(),
                            name=list_name)
        new_list.put()
        self.redirect('')

class EditListHandler(webapp.RequestHandler):
    def get(self, list_id):
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.uri)
        the_list = ToDoList.get_by_id(int(list_id))
        if not the_list:
            self.error(404)
        else:       
            self.response.out.write(render_template('list.html', {
                                       'user': user,
                                       'logout_url': logout_url,
                                       'list': the_list,
                                       'count': the_list.items.count()
        					    	}))

    def post(self, list_id):
        the_list = ToDoList.get_by_id(int(list_id))
        if not the_list:
            self.error(404)
        else:
            item_name = self.request.get('name')
            item_desc = self.request.get('desc')
            new_item  = ToDoListItem(name=item_name,
                                     desc=item_desc,
                                     list=the_list)
            new_item.put()
            self.redirect('/' + list_id)
        
class DeleteListHandler(webapp.RequestHandler):
    def post(self, list_id):
        the_list = ToDoList.get_by_id(int(list_id))
        if not the_list:
            self.error(404)
        else:
            the_list.delete()
            self.redirect('/')

class DeleteItemHandler(webapp.RequestHandler):
    def post(self, list_id, item_id):
        the_list = ToDoList.get_by_id(int(list_id))
        if not the_list:
            self.error(404)
        else:
            the_item = ToDoListItem.get_by_id(int(item_id))
            the_item.delete()
            self.redirect('/' + list_id)

class CheckItemHandler(webapp.RequestHandler):
    def post(self, list_id, item_id):
        the_list = ToDoList.get_by_id(int(list_id))
        if not the_list:
            self.error(404)
        else:
            the_item = ToDoListItem.get_by_id(int(item_id))
            the_item.checked = True
            the_item.put()
            self.redirect('/' + list_id)

class UncheckItemHandler(webapp.RequestHandler):
    def post(self, list_id, item_id):
        the_list = ToDoList.get_by_id(int(list_id))
        if not the_list:
            self.error(404)
        else:
            the_item = ToDoListItem.get_by_id(int(item_id))
            the_item.checked = False
            the_item.put()
            self.redirect('/' + list_id)

application = webapp.WSGIApplication([('/', MainHandler),
                                      (r'/(\d+)', EditListHandler),
                                      (r'/(\d+)/delete', DeleteListHandler),
                                      (r'/(\d+)/(\d+)/delete', DeleteItemHandler),
                                      (r'/(\d+)/(\d+)/check', CheckItemHandler),
                                      (r'/(\d+)/(\d+)/uncheck', UncheckItemHandler)],
                                    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()