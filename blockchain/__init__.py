# blockchain/__init__.py
from .blockchain import MedChain, get_blockchain
from .block import Block
from .validator import validate_chain, detect_tampering
