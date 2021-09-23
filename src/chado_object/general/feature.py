"""
:synopsis: Feature functions wrt general.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production import Feature
from sqlalchemy.orm.exc import NoResultFound
import logging

log = logging.getLogger(__name__)


def load_feature(self, key):
    """Load general to feature."""

    if type(self.process_data[key]['data']) is list:
        items = self.process_data[key]['data']
    else:
        items = [self.process_data[key]['data']]

    if 'uniquename' not in self.process_data[key] or not self.process_data[key]['uniquename']:
        self.critical_error(items[0], "uniquename not defined")

    for item in items:
        # lookup by uniquename
        try:
            feature = self.session.query(Feature).filter(Feature.uniquename == item[FIELD_VALUE]).one()
        except NoResultFound:
            mess = "Lookup failed to find uniquename {}".format(item[FIELD_VALUE])
            self.critical_error(item, mess)
            continue
        #  cell_line_feature_id | cell_line_id | feature_id | pub_id
        opts = {'{}_id'.format(self.table_name): self.chado.primary_id(),
                'feature_id': feature.feature_id,
                'pub_id': self.pub.pub_id}
        get_or_create(self.session,  self.alchemy_object['feature'], **opts)
