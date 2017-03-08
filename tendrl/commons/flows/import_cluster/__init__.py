# flake8: noqa

import json
import uuid
from tendrl.commons import flows
from tendrl.commons.flows.import_cluster.ceph_help import import_ceph
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster



class ImportCluster(flows.BaseFlow):
    def run(self):
        self.pre_run = []
        self.atoms = []
        self.post_run = []

        integration_id = self.parameters['TendrlContext.integration_id']
        NS.tendrl_context.integration_id = integration_id
        NS.tendrl_context.save()
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if NS.node_context.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                # create same flow for each node in node list except $this
                    payload = {"integration_id": integration_id,
                               "node_ids": [node],
                               "run": "tendrl.commons.flows.ImportCluster",
                               "status": "new",
                               "parameters": new_params,
                               "parent": self.parameters['job_id'],
                               "type": "node"
                               }

                    Job(job_id=str(uuid.uuid4()),
                        status="new",
                        payload=json.dumps(payload)).save()

        sds_name = self.parameters['DetectedCluster.sds_pkg_name']
        if "ceph" in sds_name.lower():
            import_ceph(NS.tendrl_context.integration_id)
        else:
            import_gluster(NS.tendrl_context.integration_id)
