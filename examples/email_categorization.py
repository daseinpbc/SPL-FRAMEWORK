#!/usr/bin/env python3
"""
Email Categorization Pipeline Example

This example demonstrates how to use the SPL framework for
email triage and categorization, achieving significant cost
reduction through pattern learning.

Run with:
    python examples/email_categorization.py

Expected output:
- Demonstration of cost reduction from pattern matching
- Layer-by-layer breakdown of decision making
- Final cost analysis report
"""

from spl import SPLAgent, CostTracker


def main():
    """Run email categorization example."""
    print("\n" + "=" * 60)
    print("SPL Framework - Email Categorization Example")
    print("=" * 60 + "\n")

    # Initialize agent
    agent = SPLAgent(agent_id="email_categorizer")

    # Add patterns (Layer 1) - high-confidence rules
    patterns = [
        ("urgent", r"urgent|asap|emergency", "urgent", 0.95),
        ("billing", r"invoice|payment|bill|receipt", "billing", 0.93),
        ("spam", r"unsubscribe|viagra|lottery", "spam", 0.98),
    ]

    for name, regex, category, conf in patterns:
        agent.layer1.add_pattern(name, regex, category, conf)

    print(f"Added {len(patterns)} patterns to Layer 1")
    print()

    # Sample emails for categorization
    emails = [
        {
            "user_id": "user001",
            "from": "boss@company.com",
            "subject": "URGENT: Q4 Budget Review",
            "content": "URGENT: We need to review the Q4 budget by EOD today.",
        },
        {
            "user_id": "user002",
            "from": "billing@vendor.com",
            "subject": "Invoice #12345",
            "content": "Your invoice for October services is attached. Payment due in 30 days.",
        },
        {
            "user_id": "user003",
            "from": "promo@spam.com",
            "subject": "You've WON!",
            "content": "Click here to claim your lottery prize! Unsubscribe link below.",
        },
        {
            "user_id": "user004",
            "from": "team@company.com",
            "subject": "Team lunch tomorrow",
            "content": "Hey team, lunch is at noon tomorrow at the usual place.",
        },
        {
            "user_id": "user005",
            "from": "hr@company.com",
            "subject": "ASAP: Policy Update",
            "content": "Please review the new policy ASAP and confirm receipt.",
        },
        {
            "user_id": "user006",
            "from": "finance@company.com",
            "subject": "Receipt for expenses",
            "content": "Your expense receipt has been approved for payment.",
        },
        {
            "user_id": "user007",
            "from": "newsletter@marketing.com",
            "subject": "Weekly Newsletter",
            "content": "Check out this week's updates. Click unsubscribe to stop receiving.",
        },
        {
            "user_id": "user008",
            "from": "support@vendor.com",
            "subject": "Support Ticket Update",
            "content": "Your support ticket has been updated. Please check the portal.",
        },
        {
            "user_id": "user009",
            "from": "cto@company.com",
            "subject": "Emergency: Server Down",
            "content": "EMERGENCY: Main server is down. All hands on deck!",
        },
        {
            "user_id": "user010",
            "from": "accounts@vendor.com",
            "subject": "Bill for November",
            "content": "Your November bill is ready. Total: $1,500.00",
        },
    ]

    print(f"Processing {len(emails)} emails...")
    print("-" * 60)
    print()

    # Process emails
    results = []
    for i, email in enumerate(emails, 1):
        request = {
            "user_id": email["user_id"],
            "content": f"{email['subject']} {email['content']}",
        }

        result = agent.process(request)
        results.append(result)

        layer_name = ["Reactive", "Tactical", "Deliberative"][result.layer]
        suppressed = "✓" if result.suppressed else "✗"

        print(f"Email {i}: {email['subject'][:35]:<35}")
        print(f"  From: {email['from']}")
        print(f"  Category: {result.category:<15} | Layer: {layer_name:<12}")
        print(f"  Method: {result.method:<15} | Confidence: {result.confidence:.2f}")
        print(f"  Cost: ${result.cost:.4f}         | Suppressed: {suppressed}")
        print()

    # Generate cost report
    print("-" * 60)
    print("\nCost Analysis Report")
    print("-" * 60)

    report = agent.report()

    print(f"\nTotal emails processed: {len(emails)}")
    print(f"Patterns learned: {report['patterns_learned']}")
    print(f"Layer 2 suppressions: {report['suppressions']}")
    print(f"\nCost breakdown:")
    print(f"  Total cost:           ${report['total_cost']:.4f}")
    print(f"  Cost savings:         ${report['cost_savings']:.4f}")
    print(f"  Suppression rate:     {report['suppression_rate']:.1%}")
    print(f"  Cost reduction factor: {report['cost_reduction_factor']:.1f}x")

    print("\nLayer breakdown:")
    breakdown = report["layer_breakdown"]
    for layer_name, data in breakdown.items():
        print(
            f"  {layer_name}: {data['count']} requests "
            f"({data['percentage']:.1f}%) - ${data['cost']:.4f}"
        )

    print()
    print("=" * 60)
    print("Email categorization example complete!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
