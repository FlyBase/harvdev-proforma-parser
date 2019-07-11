from bioservices import *

ch = ChEBI()
res = ch.getCompleteEntity("CHEBI:27732")
print(res.smiles)
