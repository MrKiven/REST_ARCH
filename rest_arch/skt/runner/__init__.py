# -*- coding: utf-8 -*-

from ..env import is_in_dev
from ..config import load_app_config, load_arch_config
from gunicorn.app.wsgiapp import WSGIApplication
from . import hooks


class SetAppMixin(object):
    def arch_set(self, config):
        self.cfg.set('default_proc_name', config.app_name)
        self.cfg.set('worker_class', config.worker_class)
        self.cfg.set('loglevel', 'info')
        self.cfg.set('graceful_timeout', 3)
        self.cfg.set('bind', config.get_app_binds())
        self.cfg.set('workers', config.get_app_n_workers())

        if is_in_dev():
            self.cfg.set('errorlog', '-')
        else:
            self.cfg.set('syslog', True)
            self.cfg.set('syslog_facility', 'local6')
            self.cfg.set('syslog_addr', 'unix:///dev/log#dgram')


class ArchWsgiApp(SetAppMixin, WSGIApplication):

    def init(self, parser, opts, args):
        self.app_config = load_app_config()
        self.app_uri = self.app_config.app_uri
        self.app_settings_uri = self.app_config.app_settings_uri
        self.arch_config = load_arch_config()
        args = [self.app_uri]
        self.arch_set(self.app_config)
        self.cfg.set('syslog_prefix', "{0}.wsgi".format(
            self.app_config.app_name))
        self.cfg.set('post_fork', hooks.post_fork)
        self.cfg.set('accesslog', '-')
        self.cfg.set('errorlog', '-')
        self.cfg.set('statsd_prefix',
                     "skt.wsgi.%s" % self.app_config.app_name)
        super(ArchWsgiApp, self).init(parser, opts, args)


def serve():
    ArchWsgiApp().run()
