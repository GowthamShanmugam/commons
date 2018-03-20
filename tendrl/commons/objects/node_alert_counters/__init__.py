from tendrl.commons import objects


class NodeAlertCounters(objects.BaseObject):
    def __init__(
        self,
        alert_count=0,
        node_id=None,
        *args,
        **kwargs
    ):
        super(NodeAlertCounters, self).__init__(*args, **kwargs)
        self.alert_count = alert_count
        self.node_id = node_id
        self.value = '/nodes/{0}/alert_counters'

    def render(self):
        self.value = self.value.format(
            self.node_id or NS.node_context.node_id
        )
        return super(NodeAlertCounters, self).render()
