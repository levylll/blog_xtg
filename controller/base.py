# coding=utf-8
import tornado.web
from tornado import gen
from extends.session_tornadis import Session
from config import session_keys
from model.logined_user import LoginUser


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.session = None
        self.db_session = None
        self.session_save_tag = False
        self.thread_executor = self.application.thread_executor

    @gen.coroutine
    def prepare(self):
        yield self.init_session()
        if session_keys['login_user'] in self.session:
            self.current_user = LoginUser(self.session[session_keys['login_user']])

    @gen.coroutine
    def init_session(self):
        if not self.session:
            self.session = Session(self)
            yield self.session.init_fetch()

    def save_session(self):
        self.session_save_tag = True

    @property
    def db(self):
        if not self.db_session:
            self.db_session = self.application.db_pool()
        return self.db_session

    def has_message(self):
        if session_keys['messages'] in self.session:
            return bool(self.session[session_keys['messages']])
        else:
            return False

    # category:['success','info', 'warning', 'danger']
    def add_message(self, category, message):
        item = {'category':category, 'message':message}
        if not session_keys['messages'] in self.session:
            self.session[session_keys['messages']] = [item]
        else:
            self.session[session_keys['messages']].append(item)
        self.save_session()

    def read_messages(self):
        if session_keys['messages'] in self.session:
            all_messages = self.session[session_keys['messages']]
            self.session[session_keys['messages']] = None
            self.save_session()
            return all_messages
        return None

    @gen.coroutine
    def on_finish(self):
        if self.db_session:
            self.db_session.close()
            print "db_info:", self.application.db_pool.kw['bind'].pool.status()
        if self.session is not None and self.session_save_tag:
            yield self.session.save()

