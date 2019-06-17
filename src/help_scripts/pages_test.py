"""
.. module:: app
   :synopsis: The root (main) file for the proforma parser.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""

from harvdev_utils.production import Pub
# Minimal prototype test for new proforma parsing software.
# SQL Alchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# System and logging imports
import re
import logging
import sys
import configparser
import argparse
sys.path.insert(0, '..')


parser = argparse.ArgumentParser(description='test page formats: -c /data/credentials/proforma/.secure_info')
parser.add_argument('-v', '--verbose', help='Enable verbose mode.', action='store_true')
parser.add_argument('-c', '--config', help='Specify the location of the configuration file.', required=True)

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s -- %(message)s')
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s -- %(message)s')

log = logging.getLogger(__name__)

# Import secure config variables.
config = configparser.ConfigParser()
config.read(args.config)


def create_postgres_session():
    USER = config['connection']['USER']
    PASSWORD = config['connection']['PASSWORD']
    SERVER = config['connection']['SERVER']
    DB = config['connection']['DB']

    log.info('Using server: {}'.format(SERVER))
    log.info('Using database: {}'.format(DB))

    # Create our SQL Alchemy engine from our environmental variables.
    engine_var = 'postgresql://' + USER + ":" + PASSWORD + '@' + SERVER + '/' + DB

    engine = create_engine(engine_var)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session
# to do any new script copy the above first


def split_it(page):
    """
    split pages by certain criteria
    """
    sub_pages = page.replace('--', ' ')
    sub_pages = sub_pages.replace('+', ' ')
    sub_pages = sub_pages.replace(';', ' ')

    return sub_pages.split()  # split on white space now, only pages should be left.


def simple_line(session, page):
    """
    Check for simple page numbers or varaints and if two pages make sure page1 < page2.
    return True if ant regex matches else False
    """
    simple_full_line_regex = [
        [r'^(\d+)$', 0],                    # number only
        [r'^(\d+)[p]+$', 0],                # numbers and p or pp or even ppp etc
        [r'^p+(\d+)$', 0],                  # pp then number
        [r'(\d+)--(\d+)$', 0],              # nn--nn
        [r'^s(\d+)--s(\d+)', 0],            # 's'num--'s'num
        [r'^R(\d+)--R(\d+)', 0],            # 'R'num--'R'num
    ]
    # try a few simple ones first
    page1 = None
    page2 = None
    found = False
    for regex in simple_full_line_regex:
        fields = re.search(regex[0], page)
        if fields:
            found = True
            if fields.group(1):
                page1 = int(fields.group(1))
            try:
                page2 = int(fields.group(2))
            except IndexError:
                pass
        if found:
            continue
    if found and page1 and page2:
        if page1 > page2:
            log.warning("{} is greater than {}. For'{}'. This should not be the case".format(page1, page2, page))
    if not found:
        return False
    return True


def pages_regex_test(session):
    """
    Complicated tests. Not used in production but here for sanity.
    """
    part_regexs = [
        [r'^\d+$', 0],                    # number only
        [r'^\d+[p]+$', 0],                # numbers and p or pp or even ppp etc
        [r'^[xvil]+$', 0],                # roman numerals
        [r'^n\.p\.$', 0],                 # n.p. ?? ALLOW?
        [r'^\d+[ABCa]$', 0],              # number if digits followed by either A, B or C
        [r'^[ReEsAC]\d+$', 0],            # char followed by digits
        [r'\d+\.e\d+$', 0],               # nn.'e'n
        [r'^[a-zA-Z]\d+$', 0]             # letter then numbers
    ]
    query = session.query(Pub).with_entities(Pub.pages, Pub.uniquename).filter(Pub.pages != '')
    count = 0
    for bob in query:
        if(count > 100):
            return

        page = bob.pages
        okay = simple_line(session, page)
        if not okay:
            # break up to smaller sections for testing
            simple_parts = split_it(page)
            all_subpages_found = True
            for page in simple_parts:
                sub_page_found = False
                for regex in part_regexs:
                    fields = re.search(regex[0], page)
                    if fields:
                        sub_page_found = True
                if not sub_page_found:
                    all_subpages_found = False
            if not all_subpages_found:
                count += 1
                log.info("'{}'\t\t'{}'".format(bob.pages, bob.uniquename))


if __name__ == '__main__':
    session = create_postgres_session()

    pages_regex_test(session)
