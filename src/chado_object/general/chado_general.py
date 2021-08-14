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

from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.chado_functions.organism import get_organism  # ,get_default_organism,
from harvdev_utils.chado_functions.general import general_symbol_lookup
from harvdev_utils.char_conversions import sgml_to_plain_text
from harvdev_utils.char_conversions import sub_sup_to_sgml
from harvdev_utils.char_conversions import sgml_to_unicode
from harvdev_utils.production import Synonym
from harvdev_utils.chado_functions import CodingError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
# from datetime import datetime
import logging
# import re
from harvdev_utils.production import Pub

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
        self.alchemy_object_primary = {}
        # add the chado table name i.e. grp, cell_line, library
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
            'symbol': None,  # e.g.'GG1a'
            'merge': None,
            'dissociate': None,
            'id': None,
            'is_current': None,
            'rename': None,
            'type': None,  # where type_cv and type_cvterm are found OR blank if no type.
            'org': None
        }
        self.fb_code = None

    def primary_key_name(self):
        """Get primary key name"""
        return self.chado.__table__.primary_key.columns.values()[0].name

    def add_type(self, opts):
        """ Add type to opts if exists."""
        type_name = None
        if self.creation_keys['type']:
            opts['type_id'] = get_cvterm(self.session,
                                         self.process_data[self.creation_keys['symbol']]['type_cv'],
                                         self.process_data[self.creation_keys['symbol']]['type_cvterm']).cvterm_id
            type_name = self.process_data[self.creation_keys['symbol']]['type_cvterm']
        return type_name

    def is_new(self):
        """Should object be new."""
        is_new = False
        id_key = self.creation_keys['id']
        if (id_key and self.has_data(id_key) and self.process_data[id_key]['data'][FIELD_VALUE] == 'new'):
            is_new = True
        new_key = self.creation_keys['is_current']
        if (new_key and self.has_data(new_key) and self.process_data[new_key]['data'][FIELD_VALUE] == 'n'):
            is_new = True
        return is_new

    def add_organism(self, opts):
        """Get organism."""
        organism_id = None
        if self.creation_keys['org']:
            if not self.has_data(self.creation_keys['org']):
                log.error("org is required")
                return None
            else:
                opts['organism_id'] = get_organism(self.session,
                                                   self.process_data[self.creation_keys['org']]['data'][FIELD_VALUE]).id
        return organism_id

    def initialise_object(self):
        """ Get or create an object.

        Should be replaced in individual children due to the
        wide array of none values allowed.
        """
        if self.creation_keys['rename'] and self.has_data(self.creation_keys['rename']):
            pass  # Need to code this still

        if self.creation_keys['merge'] and self.has_data(self.creation_keys['merge']):
            pass  # Need to code this still

        proforma_defined_as_new = self.is_new()
        opts = {'name': self.process_data[self.creation_keys['symbol']]['data'][FIELD_VALUE]}

        type_name = self.add_type(opts)
        organism_id = self.add_organism(opts)

        if proforma_defined_as_new:
            opts['uniquename'] = 'FB{}:temp_0'.format(self.fb_code)
            chado, is_new = get_or_create(self.session, self.alchemy_object['general'], **opts)
            self.chado = chado
            self.load_synonym(self.creation_keys['symbol'])
            if not is_new:
                log.critical("Old one returned expected a new one")
        else:
            chado = general_symbol_lookup(self.session, self.alchemy_object['general'], self.alchemy_object['synonym'],
                                          type_name,
                                          self.process_data[self.creation_keys['symbol']]['data'][FIELD_VALUE],
                                          organism_id=organism_id, cv_name='synonym type',
                                          cvterm_name='symbol', check_unique=True, obsolete='f', convert=True)

        return chado

    def get_unattrib_pub(self):
        """Get the unattributed pub."""
        if not self.unattrib_pub:
            self.unattrib_pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
        return self.unattrib_pub

    def load_synonym(self, key):
        """Load Synonym.

        yml options:
           cv:
           cvterm:
           is_current:
           remove_old: <optional> defaults to False
        NOTE:
          If is_current set to True and cvterm is symbol thensgml to plaintext is done.

        Args:
            key (string): key/field of proforma to add synonym for.
            unattrib (Bool): Add another unattributed synonym pub .
            cvterm_name (string, optional): cv synonym name, obtained from
                                            if not passed.
            overrule_removeold (Bool): wether to overrule the yml remove_old and do not do it.
        """
        if not self.has_data(key):
            return
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        is_current = self.process_data[key]['is_current']
        pub_id = self.pub.pub_id
        pubs = [pub_id]
        if 'add_unattributed_paper' in self.process_data[key] and self.process_data[key]['add_unattributed_paper']:
            unattrib_pub_id = self.get_unattrib_pub().pub_id
            if pub_id != unattrib_pub_id:
                pubs.append(unattrib_pub_id)

        # remove the current symbol if is_current is set and yaml says remove old is_current
        # ecxcept if over rule is passed.
        if 'remove_old' in self.process_data[key] and self.process_data[key]['remove_old']:
            self.remove_current_symbol(key)

        # add the new synonym
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        for item in items:
            fs = False
            for pub_id in pubs:
                fs = self.add_by_synonym_name_and_type(key, item[FIELD_VALUE], cv_name, cvterm_name, pub_id)
                if is_current and cvterm_name == 'symbol':
                    self.chado.name = sgml_to_plain_text(item[FIELD_VALUE])
                    fs.is_current = is_current

    def add_by_synonym_name_and_type(self, key, synonym_name, cv_name, cvterm_name, pub_id):
        """Add synonym"""
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)

        if not cvterm:
            raise CodingError("HarvdevError: Could not find cvterm '{}' for cv {}".format(cvterm_name, cv_name))
        synonym_sgml = None
        if 'subscript' in self.process_data[key] and not self.process_data[key]['subscript']:
            synonym_sgml = sgml_to_unicode(synonym_name)

        # Then get_create the synonym
        if not synonym_sgml:
            synonym_sgml = sgml_to_unicode(sub_sup_to_sgml(synonym_name))
        synonym_name = sgml_to_plain_text(synonym_name)
        synonym, _ = get_or_create(self.session, Synonym, type_id=cvterm.cvterm_id, name=synonym_name, synonym_sgml=synonym_sgml)
        if not synonym:
            raise CodingError("HarvdevError: Could not create synonym")
        opts = {'{}'.format(self.primary_key_name()): self.chado.id(),
                'synonym_id': synonym.synonym_id,
                'pub_id': pub_id}
        gs, is_new = get_or_create(self.session, self.alchemy_object['synonym'], **opts)
        return gs

    def load_ignore(self, key):
        """Ignore"""
        pass

    def remove_current_symbol(self, key):
        """Remove is_current for this feature_synonym.

        Make the current symbol for this feature is_current=False.
        Usually done when assigning a new symbol we want to set the old one
        to is_current = False and not to delete it.

        Args:
            session (sqlalchemy.orm.session.Session object): db connection  to use.

            object_id (int): chado obect_id.

        synonym_name (str): synonym name.

        cv_name (str):  cv name to get type of synonym

        cvterm_name (str):  cvterm name to get type of synonym

        Returns: Null

        Raises:
            CodingError: cv/cvterm lookup fails. unable to get synonym type.
        """
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            raise CodingError("HarvdevError: Could not find cvterm '{}' for cv {}".format(cvterm_name, cv_name))

        try:
            print("BOB: {}".format(self.alchemy_object['synonym']))
            print("BOB: {}".format(dir(self.alchemy_object['synonym'])))
            print("BOB: {}".format(self.alchemy_object['synonym'].grp_id))
            fss = self.synonym_lookup(cvterm)
            for fs in fss:
                fs.is_current = False
        except MultipleResultsFound:
            log.error("More than one result for BLAH id = {}".format(self.chado.id()))
            fss = self.session.query(self.alchemy_object['synonym']).join(Synonym).\
                filter(self.alchemy_object['synonym'].feature_id == self.chado.id(),
                       Synonym.type_id == cvterm.cvterm_id,
                       self.alchemy_object['synonym'].is_current == 't')
            for fs in fss:
                log.error(fs)
            raise MultipleResultsFound
        except NoResultFound:
            return
