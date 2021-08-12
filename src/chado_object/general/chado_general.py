"""
:synopsis: The Base Other None Feature Object.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>,
               Ian Longden <ianlongden@morgan.harvard.edu>

    NOTES: delete at some point once all is done

    name        | unique | name | type_id | is_ob | org |
                | name   |
    -----------------------------------------------------
    expression  | Y      | N    | N       | N     | N   |
    interaction | Y      | N    | Y       | Y     | N   |
    cell_line   | Y      | Y    | N       | N     | Y   |
    strain      | Y      | Y    | N       | Y     | Y   |
    grp         | Y      | Y    | Y       | Y     | N   |
    library     | Y      | Y    | Y       | Y     | Y   |

    CELL_LINE
    ---------

    "cell_line_c1" UNIQUE CONSTRAINT, btree (uniquename, organism_id)

                                                Table "public.cell_line"
      Column      |            Type             | Collation | Nullable |                     Default
------------------+-----------------------------+-----------+----------+-------------------------------------------------
 cell_line_id     | integer                     |           | not null | nextval('cell_line_cell_line_id_seq'::regclass)
 name             | character varying(255)      |           |          |
 uniquename       | character varying(255)      |           | not null |
 organism_id      | integer                     |           | not null |
 timeaccessioned  | timestamp without time zone |           | not null | now()
 timelastmodified | timestamp without time zone |           | not null | now()

 public | cell_line_cvterm                                                | table    | go
 public | cell_line_cvtermprop                                            | table    | go
 public | cell_line_dbxref                                                | table    | go
 public | cell_line_feature                                               | table    | go
 public | cell_line_library                                               | table    | go
 public | cell_line_libraryprop                                           | table    | go
 public | cell_line_pub                                                   | table    | go
 public | cell_line_relationship                                          | table    | go
 public | cell_line_strain                                                | table    | go
 public | cell_line_strainprop                                            | table    | go
 public | cell_line_synonym                                               | table    | go
 public | cell_lineprop                                                   | table    | go
 public | cell_lineprop_pub                                               | table    | go


   EXPRESSION
   ----------

    "expression_c1" UNIQUE CONSTRAINT, btree (uniquename)

                                        Table "public.expression"
    Column     |     Type      | Collation | Nullable |                      Default
---------------+---------------+-----------+----------+---------------------------------------------------
 expression_id | integer       |           | not null | nextval('expression_expression_id_seq'::regclass)
 uniquename    | text          |           | not null |
 md5checksum   | character(32) |           |          |
 description   | text          |           |          |

 public | expression_cvterm                                               | table    | go
 public | expression_cvtermprop                                           | table    | go
 public | expression_expression_id_seq                                    | sequence | go
 public | expression_image                                                | table    | go
 public | expression_pub                                                  | table    | go
 public | expressionprop                                                  | table    | go


    GRP
    ---

     "grp_uniquename_key" UNIQUE CONSTRAINT, btree (uniquename, type_id)

   Column    |          Type          | Collation | Nullable |               Default
-------------+------------------------+-----------+----------+-------------------------------------
 grp_id      | integer                |           | not null | nextval('grp_grp_id_seq'::regclass)
 name        | character varying(255) |           |          |
 uniquename  | text                   |           | not null |
 type_id     | integer                |           | not null |
 is_analysis | boolean                |           | not null | false
 is_obsolete | boolean                |           | not null | false

 public | grp_cvterm                                                      | table    | go
 public | grp_dbxref                                                      | table    | go
 public | grp_pub                                                         | table    | go
 public | grp_pubprop                                                     | table    | go
 public | grp_relationship                                                | table    | go
 public | grp_relationship_pub                                            | table    | go
 public | grp_relationshipprop                                            | table    | go
 public | grp_synonym                                                     | table    | go
 public | grpmember                                                       | table    | go
 public | grpmember_cvterm                                                | table    | go
 public | grpmember_pub                                                   | table    | go
 public | grpmemberprop                                                   | table    | go
 public | grpmemberprop_pub                                               | table    | go
 public | grpprop                                                         | table    | go
 public | grpprop_pub

    INTERACTION.
    ------------

  "interaction_c1" UNIQUE CONSTRAINT, btree (uniquename, type_id)

         Column     |  Type   | Collation | Nullable |                       Default
----------------+---------+-----------+----------+-----------------------------------------------------
 interaction_id | integer |           | not null | nextval('interaction_interaction_id_seq'::regclass)
 uniquename     | text    |           | not null |
 type_id        | integer |           | not null |
 description    | text    |           |          |
 is_obsolete    | boolean |           | not null | false

 public | interaction_cell_line                                           | table    | go
 public | interaction_cvterm                                              | table    | go
 public | interaction_cvtermprop                                          | table    | go
 public | interaction_expression                                          | table    | go
 public | interaction_expressionprop                                      | table    | go
 public | interaction_group                                               | table    | go
 public | interaction_group_feature_interaction                           | table    | go
 public | interaction_pub                                                 | table    | go
 public | interactionprop                                                 | table    | go
 public | interactionprop_pub                                             | table    | go


    LIBRARY
    -------

     library_c1" UNIQUE CONSTRAINT, btree (organism_id, uniquename, type_id)

 library_id       | integer                     |           | not null | nextval('library_library_id_seq'::regclass)
 organism_id      | integer                     |           | not null |
 name             | character varying(255)      |           |          |
 uniquename       | text                        |           | not null |
 type_id          | integer                     |           | not null |
 is_obsolete      | boolean                     |           | not null | false
 timeaccessioned  | timestamp without time zone |           | not null | now()
 timelastmodified | timestamp without time zone |           | not null | now()

 public | library_cvterm                                                  | table    | go
 public | library_cvtermprop                                              | table    | go
 public | library_dbxref                                                  | table    | go
 public | library_dbxrefprop                                              | table    | go
 public | library_expression                                              | table    | go
 public | library_expressionprop                                          | table    | go
 public | library_feature                                                 | table    | go
 public | library_featureprop                                             | table    | go
 public | library_grpmember                                               | table    | go
 public | library_humanhealth                                             | table    | go
 public | library_humanhealthprop                                         | table    | go
 public | library_interaction                                             | table    | go
 public | library_pub                                                     | table    | go
 public | library_relationship                                            | table    | go
 public | library_relationship_pub                                        | table    | go
 public | library_strain                                                  | table    | go
 public | library_strainprop                                              | table    | go
 public | library_synonym                                                 | table    | go
 public | libraryprop                                                     | table    | go
 public | libraryprop_pub                                                 | table    | go

  STRAIN.
  -------

  "strain_c1" UNIQUE CONSTRAINT, btree (organism_id, uniquename)

                                          Table "public.strain"
   Column    |          Type          | Collation | Nullable |                  Default
-------------+------------------------+-----------+----------+-------------------------------------------
 strain_id   | integer                |           | not null | nextval('strain_strain_id_seq'::regclass)
 name        | character varying(255) |           |          |
 uniquename  | text                   |           | not null |
 organism_id | integer                |           | not null |
 dbxref_id   | integer                |           |          |
 is_obsolete | boolean                |           | not null | false

 public | strain_cvterm                                                   | table    | go
 public | strain_cvtermprop                                               | table    | go
 public | strain_dbxref                                                   | table    | go
 public | strain_feature                                                  | table    | go
 public | strain_featureprop                                              | table    | go
 public | strain_phenotype                                                | table    | go
 public | strain_phenotypeprop                                            | table    | go
 public | strain_pub                                                      | table    | go
 public | strain_relationship                                             | table    | go
 public | strain_relationship_pub                                         | table    | go
 public | strain_synonym                                                  | table    | go
 public | strainprop                                                      | table    | go
 public | strainprop_pub                                                  | table    | go


"""
from chado_object.chado_base import ChadoObject, FIELD_VALUE
# from harvdev_utils.chado_functions import get_cvterm
# from harvdev_utils.char_conversions import sgml_to_plain_text, sgml_to_unicode
from harvdev_utils.production import (
    Grp, GrpCvterm,
    # CellLine, CellLineCvterm,
    # Library, LibraryCvterm,
    # Strain, StrainCvterm,
    # Interaction, InteractionCvterm
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.chado_functions.organism import get_default_organism, get_organism
from harvdev_utils.chado_functions.general import general_symbol_lookup
# from datetime import datetime
# from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import logging
# import re

log = logging.getLogger(__name__)


class ChadoGeneralObject(ChadoObject):
    """ChadoGeneral object."""

    def __init__(self, params):
        """Initialise the ChadoGeneral Object."""
        log.debug('Initializing ChadoGeneralObject.')

        # Initiate the parent.
        super(ChadoGeneralObject, self).__init__(params)

        # Add the chado object type i.e. Grp, CellLine, Library
        # Then GrpCvterm, etc
        self.alchemy_objects = {}

        # add the chado table name i.i. grp, cell_line, library
        self.table_name = None

        # chado object
        self.chado = None

        # Do we add unattrubuted pub
        self.unattrib_pub = None

        # Is the object new
        self.new = None

        # common start bit of all fields.
        # self.field_code = None  # e.g. for Strain "SN"

        # field extensions needed for initial get or create.
        # these will be set in the children
        self.creation_keys = {
            'symbol': None,  # e.g. GG1a
            'merge': None,
            'id': None,
            'is_current': None,
            'rename': None,
            'type': None,
            'org': None
        }

    def initialise_object(self):
        """ Get or create an object.

        Should be replaced in individual children due to the
        wide array of none values allowed.
        """
        log.error("Parent get_or_create not created yet!")
        if self.creation_keys['rename'] and self.has_data(self.creation_keys['rename']):
            pass  # Need to code this still

        if self.creation_keys['merge'] and self.has_data(self.creation_keys['merge']):
            pass  # Need to code this still

        proforma_defined_as_new = False
        id_key = self.creation_keys['id']
        if (id_key and self.has_data(id_key) and self.process_data[id_key]['data'][FIELD_VALUE] == 'new'):
            proforma_defined_as_new = True
        new_key = self.creation_keys['is_current']
        if (new_key and self.has_data(new_key) and self.process_data[new_key]['data'][FIELD_VALUE] == 'n'):
            proforma_defined_as_new = True
        opts = {'name': self.creation_keys['symbol']}

        if self.creation_keys['type']:
            if not self.has_data(self.creation_keys['type']):
                log.error("type is required")
                return None
            else:
                opts['type_id'] = get_cvterm(self.session,
                                             self.process_data[self.creation_keys['type']]['cv'],
                                             self.process_data[self.creation_keys['type']]['cvterm']).id

        if self.creation_keys['org']:
            if not self.has_data(self.creation_keys['org']):
                log.error("org is required")
                return None
            else:
                opts['organism_id'] = get_organism(self.session,
                                                   self.process_data[self.creation_keys['org']]['data'][FIELD_VALUE]).id

        chado = general_symbol_lookup(self.session, self.alchemy_object['general'], self.alchemy_object['synonym'],
                                      None,  # type
                                      self.process_data[self.creation_keys['symbol']]['data'][FIELD_VALUE], 
                                      organism_id=None, cv_name='synonym type',
                                      cvterm_name='symbol', check_unique=True, obsolete='f', convert=True)

        return chado
