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



You will need to add some functions to harvdev-utils production.py for new children i.e.
for Grp we added:-
gen_id() to GrpSynonym
id() to GrpSynonym and Grpprop

so add simlar for new ones.

"""
# from sqlalchemy.sql.schema import PrimaryKeyConstraint
from chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.chado_functions.organism import get_organism  # ,get_default_organism,
from harvdev_utils.chado_functions.general import general_symbol_lookup
from harvdev_utils.production import Synonym
from harvdev_utils.chado_functions import CodingError
from sqlalchemy.orm.exc import NoResultFound
import logging
import re
from harvdev_utils.production import Pub, Db, Dbxref

log = logging.getLogger(__name__)


class ChadoGeneralObject(ChadoObject):
    """ChadoGeneral object."""
    from chado_object.general.synonym import (
        synonym_lookup, load_synonym, add_by_synonym_name_and_type, check_old_synonym,
        remove_current_symbol, delete_synonym
    )
    from chado_object.general.prop import (
        load_generalproplist, load_generalprop, delete_prop
    )

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

        # chado object i.e. Grp, CellLine,  Library
        self.chado = None

        # Do we add unattrubuted pub
        self.unattrib_pub = None

        # Is the object new
        self.new = None

        # field extensions needed for initial get or create.
        # these will be set in the children
        # Allows for a common method to be used to do this.
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

        # list of tyoe to be removed on pub dissociation
        self.dissociate_list = []
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
        is_new = False
        id_key = self.creation_keys['id']
        if (id_key and self.has_data(id_key) and self.process_data[id_key]['data'][FIELD_VALUE] == 'new'):
            is_new = True
        new_key = self.creation_keys['is_current']
        if (new_key and self.has_data(new_key) and self.process_data[new_key]['data'][FIELD_VALUE] == 'n'):
            is_new = True
        return is_new

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
                opts['organism_id'] = get_organism(self.session,
                                                   self.process_data[self.creation_keys['org']]['data'][FIELD_VALUE]).id
        return organism_id

    def initialise_and_rename(self):
        """ """
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

    def initialise_object(self):
        """ Get or create an object.

        See creation_keys defined in the child.
        The proforma field/keys are defined in this to control.
        """
        if self.creation_keys['rename'] and self.has_data(self.creation_keys['rename']):
            return self.initialise_and_rename()

        if self.creation_keys['merge'] and self.has_data(self.creation_keys['merge']):
            pass  # Need to code this still Not needed for Grp

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
        """Ignore"""
        pass

    def load_goterm(self, key):
        """Load GO cvterms.

        Args:
            key (string): key/field of proforma to get data from.
        """
        pattern = r'^(.+)\s*;\s*GO:(\d+)$'
        for item in self.process_data[key]['data']:  # always a list
            fields = re.search(pattern, item[FIELD_VALUE])
            if fields:
                go_name = fields.group(1).strip()
                gocode = fields.group(2)
            else:
                message = "'{}' Does not fit the regex of {}/".format(item[FIELD_VALUE], pattern)
                self.critical_error(self.process_data[key]['data'][0], message)
                continue
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], go_name)
            if gocode != cvterm.dbxref.accession:
                mess = "{} matches {} but lookup gives {} instead?".format(go_name, gocode, cvterm.dbxref.accession)
                self.warning_error(self.process_data[self.process_data[key]['value']]['data'][0], mess)

            opts = {self.primary_key_name(): self.chado.id(),
                    'cvterm_id': cvterm.cvterm_id,
                    'pub_id': self.pub.pub_id}
            get_or_create(self.session, self.alchemy_object['cvterm'], **opts)

    def load_cvterm(self, key):
        """Load cvterm.

        Args:
            key (string): key/field of proforma to get data from.
        """
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        for item in items:
            try:
                cvterm = get_cvterm(self.session, self.process_data[key]['cv'], item[FIELD_VALUE])
            except CodingError:
                mess = "Could not find cv '{}', cvterm '{}'.".format(self.process_data[key]['cv'], item[FIELD_VALUE])
                self.critical_error(item, mess)
                continue
            opts = {self.primary_key_name(): self.chado.id(),
                    'cvterm_id': cvterm.cvterm_id,
                    'pub_id': self.pub.pub_id}
            get_or_create(self.session, self.alchemy_object['cvterm'], **opts)

    def load_dbxref(self, key):  # noqa
        """Load dbxref.

        yml will have defined the keys for the dbname, accession and possibly the desciption.
        See GG8a in chado_object/yml/grp.yml for example.

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
        opts = {self.primary_key_name(): self.chado.id(),
                'dbxref_id': dbx.dbxref_id}
        get_or_create(self.session, self.alchemy_object['dbxref'], **opts)

    def load_relationship(self, key):
        """Load relationship (too same type).

        Args:
            key (string): key/field of proforma to get data from.
        """
        # lookup relationship object
        for item in self.process_data[key]['data']:
            cvterm = get_cvterm(self.session, 'synonym type', 'symbol')
            # Shpuld we just do unattributed ?
            gensyn = self.session.query(self.alchemy_object['synonym']).\
                join(Synonym).join(Pub).\
                filter(Synonym.name == item[FIELD_VALUE],
                       Pub.uniquename == 'unattributed',
                       Synonym.type_id == cvterm.cvterm_id,
                       self.alchemy_object['synonym'].is_current == 't').one()

            # get cvterm for type of relatiosnhip
            cvterm = get_cvterm(self.session, self.process_data[key]['rel_cv'], self.process_data[key]['rel_cvterm'])

            # create XXX_relationship
            opts = {'type_id': cvterm.cvterm_id}
            if self.process_data[key]['subject']:
                opts['subject_id'] = gensyn.gen_id()
                opts['object_id'] = self.chado.id()
            else:
                opts['object_id'] = gensyn.gen_id()
                opts['subject_id'] = self.chado.id()
            gr, _ = get_or_create(self.session, self.alchemy_object['relationship'], **opts)

            # create XXX_relationshipPub
            opts = {'{}_relationship_id'.format(self.table_name): gr.id(),
                    'pub_id': self.pub.pub_id}
            get_or_create(self.session, self.alchemy_object['relationshippub'], **opts)

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
        id_method = getattr(chado_object_table, self.primary_key_name())
        gss = self.session.query(chado_object_table).join(Pub).\
            filter(id_method == self.chado.id(),
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
        for chado_table in (self.dissociate_list):
            self.dis_pub_table(self.alchemy_object[chado_table])
