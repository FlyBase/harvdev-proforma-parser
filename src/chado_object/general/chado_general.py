"""
:synopsis: The Base Other None Feature Object.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>

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

 GRPMEMBER
 ---------
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
# from sqlalchemy.sql.schema import PrimaryKeyConstraint
from chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.chado_functions.organism import get_organism
from harvdev_utils.chado_functions.general import general_symbol_lookup
from sqlalchemy.orm.exc import NoResultFound
import logging
from harvdev_utils.production import Pub, Db, Dbxref

log = logging.getLogger(__name__)


class ChadoGeneralObject(ChadoObject):
    """ChadoGeneral object."""
    from chado_object.general.synonym import (
        synonym_lookup, load_synonym, add_by_synonym_name_and_type, check_old_synonym,
        remove_current_symbol, delete_synonym
    )
    from chado_object.general.prop import (
        load_generalproplist, load_generalprop, delete_prop, proppubs_exist,
        bangc_prop, bangd_prop
    )
    from chado_object.general.cvterm import (
        load_cvterm, get_cvterm_by_name, delete_cvterm, load_cvtermprop
    )
    from chado_object.general.relationship import (
        load_relationship, delete_relationship, relatepubs_exist,
        bangd_relationship, bangc_relationship
    )
    from chado_object.general.feature import load_feature
    from chado_object.general.library import (
        load_library, delete_library, bangc_library, bangd_library
    )

    def __init__(self, params):
        """Initialise the ChadoGeneral Object."""
        log.debug('Initializing ChadoGeneralObject.')

        # Initiate the parent.
        super(ChadoGeneralObject, self).__init__(params)

        # Add the chado object type i.e. Grp, CellLine, Library
        # Then GrpCvterm, etc
        self.alchemy_objects = {}

        # add the chado table name i.e. grp, cell_line, library
        self.table_name = None

        # chado object i.e. Grp, CellLine,  Library
        self.chado = None

        # Do we add unattrubuted pub
        self.unattrib_pub = None

        # Is the object new
        self.new = None

        # field extensions needed for initial get or create.
        # these will be set in the children
        # Allows for a common statement to be used to do this.
        # NOTE: We have various ways of defining if something is new or not
        #       Hence is_current which has y/n normally or
        #             is_new which is either 'new' or an FBxxddddddd
        # NOTE:  no_obsolete and add_dbxrefs are not fields to check but
        #        values to be used.
        # NOTE: This dict is totally replaced and is listed here for
        #       reference mainly.
        self.creation_keys = {
            'symbol': None,  # e.g.'GG1a'
            'merge': None,
            'dissociate': None,
            'id': None,
            'uniquename': None,
            'new_uniquename': None,
            'is_current': None,
            'is_new': None,
            'rename': None,
            'type': None,  # where type_cv and type_cvterm are found OR blank if no type.
            'org': None,
            'delete': None,
            'no_obsolete': None,  # wether the chado object has an obsolete field
            'add_dbxref': 'FlyBase:uniquename'  # db name ':' and what to substitute
        }

        # list of types to be removed on pub dissociation
        self.dissociate_list = []

        # Uniquename code i.e. 'gg' for grp
        self.fb_code = None

    def primary_key_name(self):
        """Get primary key name

        This could have been put in the utils production.py and hardcoded
        but this make it more foolproof i hope.
        """
        return self.chado.__table__.primary_key.columns.values()[0].name

    def add_type(self, opts):
        """ Add type to opts if exists.

        Args:
            opts (dict): dictionary to add type to.

        Returns:
            cvterm that was looked up.
        """
        type_name = None
        if self.creation_keys['type']:
            opts['type_id'] = get_cvterm(self.session,
                                         self.process_data[self.creation_keys['symbol']]['type_cv'],
                                         self.process_data[self.creation_keys['symbol']]['type_cvterm']).cvterm_id
            type_name = self.process_data[self.creation_keys['symbol']]['type_cvterm']
        return type_name

    def is_new(self):
        """Should object be new."""
        if 'is_new' in self.creation_keys and self.creation_keys['is_new']:
            new_key = self.creation_keys['is_new']
            if (self.has_data(new_key) and self.process_data[new_key]['data'][FIELD_VALUE] == 'new'):
                return True
        if 'is_current' in self.creation_keys and self.creation_keys['is_current']:
            new_key = self.creation_keys['is_current']
            if (self.has_data(new_key) and self.process_data[new_key]['data'][FIELD_VALUE] == 'n'):
                return True
        return False

    def add_organism(self, opts):
        """Get organism.

        Args:
            opts (dict): dictionary to add organism_id to.
        Returns:
            organsim_id looked up.
        """
        organism_id = None
        if self.creation_keys['org']:
            if not self.has_data(self.creation_keys['org']):
                log.error("org is required")
                return None
            else:
                organism_id = opts['organism_id'] = get_organism(self.session,
                                                                 self.process_data[self.creation_keys['org']]['data'][FIELD_VALUE]).organism_id
        return organism_id

    def initialise_and_rename(self):
        """Initialise and rename."""
        name = self.process_data[self.creation_keys['rename']]['data'][FIELD_VALUE]
        opts = {}
        type_name = self.add_type(opts)
        organism_id = self.add_organism(opts)

        self.chado = general_symbol_lookup(self.session, self.alchemy_object['general'], self.alchemy_object['synonym'],
                                           type_name,
                                           name,
                                           organism_id=organism_id, cv_name='synonym type',
                                           cvterm_name='symbol', check_unique=True, obsolete='f', convert=True)
        # now rename it
        self.load_synonym(self.creation_keys['symbol'])
        self.chado.name = self.process_data[self.creation_keys['symbol']]['data'][FIELD_VALUE]
        return self.chado

    def init_new(self):
        """Create new object"""
        opts = {}
        self.add_type(opts)
        self.add_organism(opts)
        if 'new_uniquename' in self.creation_keys and self.creation_keys['new_uniquename']:
            unique_key = self.creation_keys['new_uniquename']
            opts['uniquename'] = self.process_data[unique_key]['data'][FIELD_VALUE]
        elif 'uniquename' in self.creation_keys and self.creation_keys['uniquename']:
            unique_key = self.creation_keys['uniquename']
            opts['uniquename'] = self.process_data[unique_key]['data'][FIELD_VALUE]
        else:
            opts['uniquename'] = 'FB{}:temp_0'.format(self.fb_code)
        self.chado, is_new = get_or_create(self.session, self.alchemy_object['general'], **opts)
        self.load_synonym(self.creation_keys['symbol'])
        if 'add_dbxref' in self.creation_keys and self.creation_keys['add_dbxref']:
            # create dbxref and connect to self.chado
            self.add_dbxref()
        if not is_new:
            log.critical("Old one returned expected a new one")

    def init_exists_already(self):
        """Get object, it exists already or at least should."""
        opts = {}
        type_name = self.add_type(opts)
        organism_id = self.add_organism(opts)

        if 'no_obsolete' in self.creation_keys and self.creation_keys['no_obsolete']:
            obsolete = None
        else:
            obsolete = 'f'
        try:
            # lookup by synonym
            if self.has_data(self.creation_keys['symbol']):
                syn_name = self.process_data[self.creation_keys['symbol']]['data'][FIELD_VALUE]
                self.chado = general_symbol_lookup(self.session,
                                                   self.alchemy_object['general'], self.alchemy_object['synonym'],
                                                   type_name,
                                                   syn_name,
                                                   organism_id=organism_id,
                                                   cv_name='synonym type',
                                                   cvterm_name='symbol', check_unique=True, obsolete=obsolete, convert=True)
                if 'uniquename' in self.creation_keys and self.has_data(self.creation_keys['uniquename']):
                    stated_uniquename = self.process_data[self.creation_keys['uniquename']]['data'][FIELD_VALUE]
                    if stated_uniquename != self.chado.uniquename:
                        mess = "lookup by the synonym '{}' found unique '{}' BUT uniquename stated to be '{}'.".\
                            format(syn_name, self.chado.uniquename, stated_uniquename)
                        self.critical_error(self.process_data[self.creation_keys['symbol']]['data'], mess)
            elif self.has_data(self.creation_keys['uniquename']):
                unique_key = self.creation_keys['uniquename']
                opts['uniquename'] = self.process_data[unique_key]['data'][FIELD_VALUE]
                self.chado, is_new = get_or_create(self.session, self.alchemy_object['general'], **opts)
                if is_new:
                    mess = "Could not find unique name '{}' and type '{}'".\
                        format(opts['uniquename'], type_name)
                    self.critical_error(self.process_data[self.creation_keys['uniquename']]['data'], mess)
            # else:
            #    mess = "No symbol or uniquename data, so cannot initiate chado object"
            #    self._
            #    self.critical_error(self.process_data[self.creation_keys['symbol']]['data'], mess)
        except NoResultFound:
            mess = "Could not find '{}' in synonym lookup.".format(self.process_data[self.creation_keys['symbol']]['data'][FIELD_VALUE])
            self.critical_error(self.process_data[self.creation_keys['symbol']]['data'], mess)
            return None

    def initialise_object(self):
        """ Get or create an object.

        See creation_keys defined in the child.
        The proforma field/keys are defined in this to control.
        """
        if self.creation_keys['rename'] and self.has_data(self.creation_keys['rename']):
            return self.initialise_and_rename()

        if self.creation_keys['merge'] and self.has_data(self.creation_keys['merge']):
            # Need to code this still, Not needed for Grp and that is the only one done
            # at present. Delete this message when code has bben addded.
            log.critical("Merging not coded yet.")

        proforma_defined_as_new = self.is_new()

        if proforma_defined_as_new:
            self.init_new()
        else:
            self.init_exists_already()

    def add_dbxref(self):
        """Add dbxref and connect"""
        db_name, acc_format = self.creation_keys['add_dbxref'].split(':')
        if 'uniquename' in self.creation_keys['add_dbxref']:
            acc_format = self.creation_keys['add_dbxref']
            acc = acc_format.replace('uniquename', self.chado.uniquename)
        else:
            mess = "Harv dev problem: dbxref does not have uniquename in specification"
            log.critical_error(self.process_data[self.creation_keys['symbol']]['data'], mess)
            exit(-1)

        db = self.session.query(Db).filter(Db.name == db_name).one()
        dbxref, _ = get_or_create(self.session, Dbxref,
                                  accession=acc, db_id=db.db_id)
        # add this to self.chado.
        opts = {self.primary_key_name(): self.chado.primary_id(),
                'dbxref_id': dbxref.dbxref_id}
        get_or_create(self.session, self.alchemy_object['dbxref'], **opts)

    def get_unattrib_pub(self):
        """Get the unattributed pub."""
        if not self.unattrib_pub:
            self.unattrib_pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
        return self.unattrib_pub

    def get_pubs(self, key):
        """Get list of pubs to use.

        chado_object/yml/xxx_yml has info on what pubs are allowed
        so process this info and pass on what is needed.

        Args:
           key (string): proforma field/key.
        Returns:
           List of pub_ids.
        """
        pub_id = self.pub.pub_id
        pubs = [pub_id]
        unattrib_pub_id = self.get_unattrib_pub().pub_id
        if 'add_unattributed_paper' in self.process_data[key] and self.process_data[key]['add_unattributed_paper']:
            if pub_id != unattrib_pub_id:
                pubs.append(unattrib_pub_id)
        if 'add_unattributed_paper_only' in self.process_data[key] and self.process_data[key]['add_unattributed_paper_only']:
            pubs = [unattrib_pub_id]
        return pubs

    def load_ignore(self, key):
        """Ignore.

        Some fields/keys are dealt with by other functions. So this is okay for some.
        i.e. those keys needed for creation of the initial object or part of a set.
        """
        pass

    def load_dbxref(self, key):  # noqa
        """Load dbxref.

        yml will have defined the keys for the dbname, accession and possibly the desciption.
        See GG8a in chado_object/yml/grp.yml for example.

        Usually done as part of a set. In the yml file the fields.keys to use for the dbname and
        accession and maybe the description are defined. See GG8a as an example.
        Args:
            key (string): key/field of proforma to get data from.
        """
        if not self.has_data(key):
            return
        mess = None
        try:
            db_name = self.process_data[self.process_data[key]['dbname']]['data'][FIELD_VALUE]
            acc = self.process_data[self.process_data[key]['accession']]['data'][FIELD_VALUE]
        except KeyError:
            try:
                mess = "dbname Field '{}' and accession Field '{}' REQUIRED for this.".\
                    format(self.process_data[key]['dbname'], self.process_data[key]['accession'])
            except KeyError:
                mess = "Contact Harvdev: fields not defined for accession and description"
        if mess:
            self.critical_error(self.process_data[key]['data'], mess)
            return

        # lookup db make sure it exists!
        try:
            db = self.session.query(Db).filter(Db.name == db_name).one()
        except NoResultFound:
            mess = "Could not find db '{}' in the database.".format(db_name)
            self.critical_error(self.process_data[key]['data'], mess)
            return

        # create/get the dbxref.
        opts = {'db_id': db.db_id,
                'accession': acc}
        dbx, _ = get_or_create(self.session, Dbxref, **opts)
        if 'description' in self.process_data[key]:
            desc_key = self.process_data[key]['description']
            dbx.description = self.process_data[desc_key]['data'][FIELD_VALUE]

        # add this to self.chado.
        opts = {self.primary_key_name(): self.chado.primary_id(),
                'dbxref_id': dbx.dbxref_id}
        get_or_create(self.session, self.alchemy_object['dbxref'], **opts)

    def make_obsolete(self, key):
        """ Make self obsolete.

        Args:
            key (string): Proforma field key
        """
        if not self.has_data(key) or self.process_data[key]['data'][FIELD_VALUE] != 'y':
            return
        self.chado.is_obsolete = True

    def dis_pub_table(self, chado_object_table):
        """Dissociate pub and self.chado from table.

        Args:
            key (string): Proforma field key
            chado_object_table: <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
        """
        id_statement = getattr(chado_object_table, self.primary_key_name())
        gss = self.session.query(chado_object_table).join(Pub).\
            filter(id_statement == self.chado.primary_id(),
                   Pub.pub_id == self.pub.pub_id)
        for gs in gss:
            self.session.delete(gs)

    def dis_pub(self, key):
        """Dissociate pub and grp from all self.chado objects.

        Args:
            key (string): Proforma field key
        """
        if not self.has_data(key) or self.process_data[key]['data'][FIELD_VALUE] != 'y':
            return
        # dissociate_list has a list of tables that on dissociate from pub
        # need to be deleted.
        for chado_table in (self.dissociate_list):
            self.dis_pub_table(self.alchemy_object[chado_table])
