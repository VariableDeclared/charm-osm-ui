#!/usr/bin/env python3

import sys
sys.path.append('lib')
from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState
from interface_mysql import MySQLClient
from oci_image import OCIImageResource


class OSMUIK8sCharm(CharmBase):
    state = StoredState()

    def __init__(self, framework, key):
        super.__init__(framework, key)
        self.state.set_defaults(is_started=False)
        self.mysql = MySQLClient(self, 'mysql')
        self.ui_image = OCIImageResource(self, 'osm_ui_image')
        # TODO(pjds): How can we set the maintenance status?
        self.framework.observe(
            self.mysql.on.database_available,
            self.configure_pod
        )
        self.framework.observe(
            self.mysql.on.database_changed,
            self.configure_pod
        )
        self.framework.observe(self.on.config_changed, self.configure_pod)

    def configure_pod(self):
        """Make pod specification for Kubernetes and submit it to the framework

        Returns:
            None
        """

        md = self.framework.meta
        cfg = self.framework.model.config
        client = self.mysql
        db = client.database()
        pod_spec = {
            'containers': [{
                'name': f"{md.get('name')}",
                'imageDetails': {
                    'imagePath': f"{self.ui_image.image_path}",
                    'username': f"image_info.username",
                    'password': f"image_info.passwor",
                },
                'ports': [{
                    'containerPort': f"{cfg.get('advertised-port')}",
                    'protocol': 'TCP'
                }],
                'config': {
                    'ALLOW_ANONYMOUS_LOGIN': 'yes',
                    'OSM_SERVER': {
                        'nbi_host': None
                    },
                    'OSMUI_SQL_DATABASE_URI':
                    f"mysql://root:{db.password}@{db.host}:{db.port}/{db.name}"
                },
                'readinessProbe': {
                    'tcpSocket': {
                        'port': f"{cfg.get('advertised-port')}"
                    },
                    'periodSeconds': 10,
                    'timeoutSeconds': 5,
                    'successThreshold': 1,
                    'failureThreshold': 3
                },
                'livenessProbe': {
                    'tcpSocket': {
                        'port': f"{cfg.get('advertised-port')}"
                    },
                    'initialDelaySeconds': 30,
                    'periodSeconds': 10,
                    'timeoutSeconds': 5,
                    'successThreshold': 1,
                    'failureThreshold': 3
                }
            }]
        }

        self.model.set_spec(pod_spec)


if __name__ == "__main__":
    main(OSMUIK8sCharm)
