# Cerberus and yaml
from validation.validator_base import ValidatorBase

# Additional tools for validation
import re

# System and logging imports
import os
import sys
import logging
log = logging.getLogger(__name__)

class PubValidator(ValidatorBase):
    def __init__(self,schema):
        super().__init__(schema) # Initialize the super class from within the subclass

    def get_type():
        return('PubValidator')