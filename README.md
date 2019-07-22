[![Build Status](https://travis-ci.com/FlyBase/harvdev-proforma-parser.svg?token=7Nvc5gEdzuNraK13EL3s&branch=develop)](https://travis-ci.com/FlyBase/harvdev-proforma-parser)

# Harvdev Proforma Parser

## Requirements
- A clone of this repository.
- Appropriate `config.cfg` file with correct parameters (contact Harvdev for a copy).
- Access to an instance of Chado.

## Running the parser

Main command: `src/app.py`

Flags:
- `-v` Enable verbose mode
- `-c` Specify config file location
- `-l` Load type (`test` or `production`)
  -  Using `test` will rollback any changes while `production` will commit them.
- `-d` Directory of proforma files to load.

Example commands:

- `python3 src/app.py -v -c ../credentials/config.cfg -d ../proforma/input/ -l test`

- `python3 src/app.py -v -c ../credentials/config.cfg -d ../proforma/input/ -l production`

**Please be sure NOT to store the config.cfg file in this repository.**

## Testing

WIP, coming soon.