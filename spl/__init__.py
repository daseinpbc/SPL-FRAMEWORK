"""
SPL Framework - Subsumption Pattern Learning

Hierarchical foundation model agent architecture that reduces costs 
by 10-50x through intelligent suppression of expensive foundation model calls.

Grounded in Ronald Arkin's behavior-based robotics and Rodney Brooks' 
subsumption architecture.
"""

from .agent import SPLAgent
from .layer0_reactive import Layer0Reactive
from .layer1_tactical import Layer1Tactical
from .layer2_deliberative import Layer2Deliberative
from .cost_tracker import CostTracker
from .mcp_integration import MCPClient

__version__ = "3.1.0"
__author__ = "Pamela Cuce, Shreyas G"
__email__ = "pamela@dasein.works, shreyas@dasein.works"

__all__ = [
    "SPLAgent",
    "Layer0Reactive", 
    "Layer1Tactical",
    "Layer2Deliberative",
    "CostTracker",
    "MCPClient",
]
