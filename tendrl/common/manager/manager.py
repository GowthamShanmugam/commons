import abc
import gevent.event
import gevent.greenlet
import logging
import six

from tendrl.common.manager.job_sync import SyncJobThread

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class SyncStateThread(gevent.greenlet.Greenlet):
    def __init__(self, manager):
        super(SyncStateThread, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    @abc.abstractmethod
    def _run(self):
        raise NotImplementedError(
            'define the function on_pull to use this class'
        )


@six.add_metaclass(abc.ABCMeta)
class Manager(object):
    def __init__(
        self,
        name,
        integration_id,
        config,
        events,
        persister,
        defs_dir
    ):
        self.name = name
        self._config = config
        self.integration_id = integration_id
        self._complete = gevent.event.Event()
        self._user_request_thread = SyncJobThread(self)
        self._discovery_thread = events
        self.persister = persister
        self.defs_dir = defs_dir

    def stop(self):
        LOG.info("%s stopping" % self.__class__.__name__)
        self._user_request_thread.stop()
        self._discovery_thread.stop()

    def _recover(self):
        LOG.debug("Recovered server")
        pass

    def start(self):
        LOG.info("%s starting" % self.__class__.__name__)
        self._user_request_thread.start()
        self._discovery_thread.start()
        self.persister.start()

    def join(self):
        LOG.info("%s joining" % self.__class__.__name__)
        self._user_request_thread.join()
        self._discovery_thread.join()
        self.persister.join()

    @abc.abstractmethod
    def on_pull(self, raw_data, cluster_id):
        raise NotImplementedError(
            'define the function on_pull to use this class'
        )
