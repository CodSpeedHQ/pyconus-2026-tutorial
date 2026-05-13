"""Your Round 3 solution — DNA sequence matcher.

#**Edit this file.** It currently delegates to ``baseline.py`` so everything
#passes out of the box. Replace the body of ``find_matches`` with your
#own faster implementation.


#import numpy as np
#import threading

#def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
	
#	Returns ``[(record_id, [positions...]), ...]`` in file order.
#	"""
#	# Step 1: read the whole FASTA file as text and decode the pattern so the
#	# search below can use a single ``str`` API.
#	pattern_str = pattern.decode("ascii")


#	data = np.loadtxt(fasta_path, dtype=str, delimiter="/n")
#	data = 

#	data = {s.split(delimiter)[0].strip(): s.split('>')[1].strip() for s in sequencet}
	
#	positions: list[int] = []	
#	data = np.array(final_list)
	
#	mask = (data == pattern)
#	count = np.count_nonzero(mask)


#from __future__ import annotations

#"""Fast Round 3 solution: DNA sequence matcher."""



from __future__ import annotations

import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor 

_NEWLINE = b"\n"



def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    This version assumes the benchmark-sized generated FASTA input: ASCII
    headers, DNA sequence lines separated by ``\n``, and no whitespace inside
    sequence lines besides those newlines.
    """
    if not pattern:
        return []

    pattern_values = np.frombuffer(pattern, dtype=np.uint8)
    pattern_len = len(pattern)

    with open(fasta_path, "rb") as file:
        data = file.read()

    matches: list[tuple[str, list[int]]] = []
    for record in data.split(b">")[1:]:
        record_id, _, wrapped_sequence = record.partition(_NEWLINE)
        sequence = wrapped_sequence.replace(_NEWLINE, b"")
        sequence_len = len(sequence)
        if sequence_len < pattern_len:
            continue

        sequence_values = np.frombuffer(sequence, dtype=np.uint8)
        positions_mask = (
            sequence_values[: sequence_len - pattern_len + 1] == pattern_values[0]
        )
        for pattern_index in range(1, pattern_len):
            positions_mask &= (
                sequence_values[
                    pattern_index : sequence_len - pattern_len + 1 + pattern_index
                ]
                == pattern_values[pattern_index]
            )

        positions = np.nonzero(positions_mask)[0]
        if positions.size:
            matches.append((record_id.decode("ascii"), positions.tolist()))

    return matches
	
	

