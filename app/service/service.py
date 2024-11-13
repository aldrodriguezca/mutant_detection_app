import hashlib
import logging
from typing import List, Dict, Any, Optional
from db.mongodb import dna_collection

logger = logging.getLogger(__name__)

def get_human_type_count(is_mutant: Optional[bool]=None) -> int:
    """
    Perform counting of DNA-type sequences stored in DB.

    Returns:
        Number indicating number of stored sequences corresponding to certain 
        DNA type.
    """
    return dna_collection.count_documents({"is_mutant": is_mutant})

def get_stats() -> Dict[str, Any]:
    """
    Query the stats of existing DNA-sequences stored in DB.

    Returns:
        Dictionary containing the count for human, mutant, and mutant-ratio of existing 
        DNA sequences.
    """
    human_count = get_human_type_count(False)
    mutant_count = get_human_type_count(True)
    ratio = human_count / (human_count + mutant_count)

    return {
        "count_human_dna": human_count,
        "count_mutant_dna": mutant_count,
        "ratio": ratio
    }

def verify_and_save_sequence(dna_object: Dict[str, Any]) -> bool:
    """
    Verifies whether the input DNA-sequence corresponds to a human or mutant being. 
    Also stores the corresponding result in DB.

    Args:
        dna_object: Dict[str, Any]
        Dictionary containing DNA-data

    Returns:
        Boolean indicating whether the provided DNA sequence corresponds to mutant or human.
    """
    seq_hash = get_sequence_hash(dna_object)
    is_mutant = is_mutant_dna(dna_object['dna'])
    persist_sequence(seq_hash, dna_object['dna'], is_mutant)
    return is_mutant

def persist_sequence(hash: str, dna_seq: List[str], is_mutant: bool):
    if not bool(dna_collection.find_one({"sequence_id": hash})):
        dna_collection.insert_one({
            "sequence_id": hash,
            "dna_sequence": ''.join(dna_seq),
            "is_mutant": is_mutant
        })
        logger.info("New DNA-record")
    else:
        logger.info("Existent previous record")

def get_sequence_hash(dna_object: Dict[str, Any]) -> str:
    """ Return a hash for the input DNA sequence

    Args:
        dna_object: Dict[str, Any]
            Dictionary containing input data for DNA sequence.

    Returns:
        String containing hashed contend for input DNA sequence
    """
    plain_sequence = ''.join(dna_object['dna'])
    h = hashlib.new('sha512', usedforsecurity=False)
    h.update(str.encode(plain_sequence))
    hashed_seq = h.hexdigest()
    
    return hashed_seq

def is_mutant_dna(dna_matrix: List[str]) -> bool :
    """Verifiy the DNA-sequence data in order to see if the mutant-defining criteria is met

    Args:
        dna_matrix: List[str]
            List of strings containing DNA-strings

    Returns:
        Boolean value indicating whether the provided dna sequence (matrix) 
        corresponds to a mutant (True) or human (False).
    """

    repeated_seqs = 0
    seq_len_criteria = 4
    mutant_threshold = 1

    W = range(len(dna_matrix))
    H = range(len(dna_matrix[0]))
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    dir = 0
    repeated_seqs = 0
    
    while dir < len(directions) and repeated_seqs <= mutant_threshold:
        scan_path = []
        dx, dy = directions[dir]
        dir +=1
        
        if dx > 0:
            scan_path += [(0, y) for y in H]
            
        if dy > 0:
            scan_path += [(x, 0) for x in W]
            
        if dy < 0:
            scan_path += [(x, H[-1]) for x in W]
            
        for sx, sy in scan_path:
            seq = 0; mark = None
            x, y = sx, sy
            
            while x in W and y in H:
                if dna_matrix[x][y] == mark:
                    seq += 1
                else:
                    mark = dna_matrix[x][y]
                    seq = 1
                if mark is not None and seq >= seq_len_criteria:
                    repeated_seqs += 1

                if repeated_seqs > mutant_threshold:
                    return True
                x, y = x + dx, y + dy

    return repeated_seqs > mutant_threshold

