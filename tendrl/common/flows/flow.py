import etcd
import logging

from tendrl.common.flows.base_flow import BaseFlow
from tendrl.common.flows import utils

LOG = logging.getLogger(__name__)


class Flow(BaseFlow):
    def __init__(
        self,
        name,
        atoms,
        help,
        enabled,
        inputs,
        pre_run,
        post_run,
        type,
        uuid,
        parameters,
        job,
        config,
        definitions
    ):
        self.name = name
        self.atoms = atoms
        self.help = help
        self.enabled = enabled
        self.inputs = inputs
        self.pre_run = pre_run
        self.post_run = post_run
        self.type = type
        self.uuid = uuid
        self.parameters = parameters
        self.job = job
        self.config = config
        self.definitions = definitions

        self.parameters.update({'log': []})
        etcd_kwargs = {
            'port': int(self.config.get("common", "etcd_port")),
            'host': self.config.get("common", "etcd_connection")
        }

        self.etcd_client = etcd.Client(**etcd_kwargs)
        self.parameters.update({'etcd_client': self.etcd_client})

    def run(self):
        post_atom = None
        pre_atom = None
        the_atom = None

        # Execute the pre runs for the flow
        LOG.info("Starting execution of pre-runs for flow: %s" %
                 self.job['run'])
        for mod in self.pre_run:
            ret_val = self.execute_atom(mod, self.definitions)

            if not ret_val:
                LOG.error("Failed executing pre-run: %s for flow: %s" %
                          (pre_atom, self.job['run']))
                raise Exception(
                    "Error executing pre run function: %s for flow: %s" %
                    (pre_atom, self.job['run'])
                )
            else:
                LOG.info("Successfully executed pre-run: %s for flow: %s" %
                         (pre_atom, self.job['run']))

        # Execute the atoms for the flow
        LOG.info("Starting execution of atoms for flow: %s" %
                 self.job['run'])
        for atom in self.atoms:
            ret_val = self.execute_atom(atom, self.definitions)

            if not ret_val:
                LOG.error("Failed executing atom: %s on flow: %s" %
                          (the_atom, self.job['run']))
                raise Exception(
                    "Error executing atom: %s on flow: %s" %
                    (atom, self.job['run'])
                )
            else:
                LOG.info('Successfully executed atoms for flow: %s' %
                         self.job['run'])

        # Execute the post runs for the flow
        LOG.info("Starting execution of post-runs for flow: %s" %
                 self.job['run'])
        for mod in self.post_run:
            ret_val = self.execute_atom(mod, self.definitions)

            if not ret_val:
                LOG.error("Failed executing post-run: %s for flow: %s" %
                          (post_atom, self.job['run']))
                raise Exception(
                    "Error executing post run function: %s" % post_atom
                )
            else:
                LOG.info("Successfully executed post-run: %s for flow: %s" %
                         (post_atom, self.job['run']))

    def extract_atom_details(self, atom_name, definitions):
        namespace = atom_name.split('.objects.')[0]
        object_name = atom_name.split('.objects.')[1].split('.atoms.')[0]
        atom = definitions[namespace]['objects'][object_name]['atoms']
        [atom_name.split('.')[-1]]
        return atom.get('name'), atom.get('enabled'), atom.get('help'), \
            atom.get('inputs'), atom.get('outputs'), atom.get('uuid')

    def execute_atom(self, mod, definitions):
        class_name = utils.to_camel_case(mod.split(".")[-1])
        if "tendrl" in mod and "atoms" in mod:
            atom_name, enabled, help, inputs, outputs, uuid = \
                self.extract_atom_details(mod, self.definitions)
            exec("from %s import %s as the_atom" % (
                mod.lower().strip("."),
                class_name.strip("."))
            )

            ret_val = the_atom(
                atom_name,
                enabled,
                help,
                inputs,
                outputs,
                uuid
            ).run(self.parameters)

            return ret_val
        return False
