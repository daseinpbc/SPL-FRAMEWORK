#!/usr/bin/env python3
"""
Multi-Agent Network Example

This example demonstrates how multiple SPL agents can share
learned patterns to achieve network-wide cost reduction.

Run with:
    python examples/multi_agent_network.py

Expected output:
- Agent A learns patterns (uses Layer 2 / foundation model)
- Agents B and C reuse patterns from Agent A (Layer 1)
- Significant cost reduction through pattern sharing
"""

from spl import SPLAgent


class SharedStateServer:
    """
    Simulated shared state server for multi-agent coordination.

    In production, this would be implemented using Redis or
    a similar distributed state store.
    """

    def __init__(self):
        """Initialize shared state."""
        self.global_state = {
            "learned_patterns": {},
            "network_stats": {"total_requests": 0, "total_cost": 0.0},
        }

    def get_state(self):
        """Get reference to global state."""
        return self.global_state


def main():
    """Run multi-agent network example."""
    print("\n" + "=" * 60)
    print("SPL Framework - Multi-Agent Network Example")
    print("=" * 60 + "\n")

    # Create shared state server
    shared_server = SharedStateServer()
    shared_state = shared_server.get_state()

    # Create multiple agents sharing the same state
    agents = {
        "Agent A": SPLAgent(agent_id="agent_a", shared_state=shared_state),
        "Agent B": SPLAgent(agent_id="agent_b", shared_state=shared_state),
        "Agent C": SPLAgent(agent_id="agent_c", shared_state=shared_state),
    }

    print(f"Created {len(agents)} agents with shared state")
    print()

    # Test emails - variety of categories
    test_emails = [
        # Urgent emails
        ("URGENT: Meeting moved to 3pm", "urgent"),
        ("URGENT: Budget review needed ASAP", "urgent"),
        ("Emergency: System outage in progress", "urgent"),
        # Billing emails
        ("Invoice #12345 for October", "billing"),
        ("Payment received: $5000", "billing"),
        ("Your bill for November services", "billing"),
        # Spam emails
        ("You've won a free iPad! Click here", "spam"),
        ("Unsubscribe from our mailing list", "spam"),
        # Other emails
        ("Team lunch tomorrow at noon", "other"),
        ("Weekly status update", "other"),
    ]

    # ========================================
    # Phase 1: Agent A learns patterns
    # ========================================
    print("=" * 60)
    print("PHASE 1: Agent A Learning")
    print("=" * 60)
    print("Agent A processes emails and learns patterns...")
    print("-" * 60)
    print()

    agent_a = agents["Agent A"]

    # Agent A processes first batch (will use Layer 2 for new patterns)
    for i, (content, expected) in enumerate(test_emails[:4], 1):
        request = {"user_id": f"user{i:03d}", "content": content}
        result = agent_a.process(request)

        layer_name = ["Reactive", "Tactical", "Deliberative"][result.layer]
        print(f"Email {i}: {content[:40]:<40}")
        print(f"  Result: {result.category:<10} | Layer: {layer_name}")
        print(f"  Method: {result.method:<15} | Cost: ${result.cost:.4f}")
        print()

    report_a = agent_a.report()
    print(f"Agent A Summary:")
    print(f"  Patterns learned: {report_a['patterns_learned']}")
    print(f"  Total cost: ${report_a['total_cost']:.4f}")
    print()

    # ========================================
    # Phase 2: Agents B & C use shared patterns
    # ========================================
    print("=" * 60)
    print("PHASE 2: Agents B & C Using Shared Patterns")
    print("=" * 60)
    print("Agents B & C process similar emails using learned patterns...")
    print("-" * 60)
    print()

    for agent_name in ["Agent B", "Agent C"]:
        agent = agents[agent_name]
        print(f"\n{agent_name}:")
        print("-" * 40)

        # Process a subset of emails
        for i, (content, expected) in enumerate(test_emails[4:7], 1):
            request = {"user_id": f"user{i+10:03d}", "content": content}
            result = agent.process(request)

            layer_name = ["Reactive", "Tactical", "Deliberative"][result.layer]
            suppressed = "Yes" if result.suppressed else "No"
            print(f"  Email: {content[:35]:<35}")
            print(f"    Result: {result.category:<10} | Layer: {layer_name}")
            print(f"    Suppressed L2: {suppressed:<5} | Cost: ${result.cost:.4f}")
            print()

    # ========================================
    # Phase 3: All agents at scale
    # ========================================
    print("=" * 60)
    print("PHASE 3: All Agents at Scale")
    print("=" * 60)
    print("All agents process remaining emails with pattern sharing...")
    print("-" * 60)
    print()

    # Process remaining emails across all agents
    for content, expected in test_emails[7:]:
        for agent_name, agent in agents.items():
            request = {"user_id": "user999", "content": content}
            result = agent.process(request)

    # ========================================
    # Network-wide Report
    # ========================================
    print("=" * 60)
    print("NETWORK-WIDE REPORT")
    print("=" * 60)
    print()

    total_cost = 0.0
    total_suppressions = 0
    total_patterns = 0

    print("Individual Agent Reports:")
    print("-" * 60)

    for agent_name, agent in agents.items():
        report = agent.report()
        total_cost += report["total_cost"]
        total_suppressions += report["suppressions"]
        total_patterns = max(total_patterns, report["patterns_learned"])

        print(f"\n{agent_name} ({agent.agent_id}):")
        print(f"  Total cost: ${report['total_cost']:.4f}")
        print(f"  Suppressions: {report['suppressions']}")
        print(f"  Suppression rate: {report['suppression_rate']:.1%}")

    # Calculate baseline (if all requests went to Layer 2)
    total_requests = sum(
        agent.cost_tracker.total_requests for agent in agents.values()
    )
    baseline_cost = total_requests * 0.01
    savings = baseline_cost - total_cost
    reduction_factor = baseline_cost / total_cost if total_cost > 0 else float("inf")

    print()
    print("-" * 60)
    print("Network Summary:")
    print("-" * 60)
    print(f"  Total agents: {len(agents)}")
    print(f"  Total requests: {total_requests}")
    print(f"  Shared patterns: {len(shared_state['learned_patterns'])}")
    print()
    print(f"  Baseline cost (all L2): ${baseline_cost:.4f}")
    print(f"  Actual cost:            ${total_cost:.4f}")
    print(f"  Total savings:          ${savings:.4f}")
    print(f"  Cost reduction factor:  {reduction_factor:.1f}x")

    print()
    print("=" * 60)
    print("KEY INSIGHT:")
    print("Patterns learned by Agent A are automatically available")
    print("to Agents B & C through the shared state, enabling")
    print("network-wide cost reduction without redundant learning.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
