import abc

import etcd
import six

from tendrl.commons.central_store import utils as cs_utils


@six.add_metaclass(abc.ABCMeta)
class BaseObject(object):
    def __init__(self):
        self.load_definition()

    def __new__(cls, *args, **kwargs):

        super_new = super(BaseObject, cls).__new__
        if super_new is object.__new__:
            instance = super_new(cls)
        else:
            instance = super_new(cls, *args, **kwargs)

        return instance

    def load_definition(self):
        self._defs = self._ns.get_obj_definition(self.__class__.__name__)

    def save(self):
        try:
            current_obj = self.load()
            for attr, val in self.__dict__.iteritems():
                if attr in ["defs"]:
                    continue
                if val is None:
                    continue
                if attr.startswith("_"):
                    continue

                setattr(current_obj, attr, val)

            cls_etcd = cs_utils.to_etcdobj(self._etcd_cls, current_obj)
        except etcd.EtcdKeyNotFound as ex:
            cls_etcd = cs_utils.to_etcdobj(self._etcd_cls, self)

        getattr(NS.central_store_thread, "save_%s" %
                self.__class__.__name__.lower())(cls_etcd())

    def load(self):
        cls_etcd = cs_utils.to_etcdobj(self._etcd_cls, self)
        result = NS.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()


@six.add_metaclass(abc.ABCMeta)
class BaseAtom(object):
    def __init__(self, parameters=None):
        self.parameters = parameters
        self.load_definition()

    def load_definition(self):
        self._defs = self._ns.get_atom_definition(self.obj.__name__,
                                                      self.__class__.__name__)

    @abc.abstractmethod
    def run(self):
        raise AtomNotImplementedError(
            'define the function run to use this class'
        )

    def __new__(cls, *args, **kwargs):

        super_new = super(BaseAtom, cls).__new__
        if super_new is object.__new__:
            instance = super_new(cls)
        else:
            instance = super_new(cls, *args, **kwargs)

        return instance


class AtomNotImplementedError(NotImplementedError):
    def __init___(self, err):
        self.message = "run function not implemented. %s".format(err)


class AtomExecutionFailedError(Exception):
    def __init___(self, err):
        self.message = "Atom Execution failed. Error:" + \
                       " %s".format(err)
