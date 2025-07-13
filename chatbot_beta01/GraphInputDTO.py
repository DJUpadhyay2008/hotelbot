# dtos.py
from dataclasses import dataclass

@dataclass
class GraphInputDTO:
    """
    A Data Transfer Object (DTO) to encapsulate input for the graph.
    """
    prompt: str
    session_id: str