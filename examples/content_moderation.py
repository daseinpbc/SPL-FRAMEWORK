#!/usr/bin/env python3
"""
Content Moderation Example

This example demonstrates how to use the SPL framework for
content moderation, using Layer 0 for blocklist enforcement
and Layer 1 for pattern-based content classification.

Run with:
    python examples/content_moderation.py

Expected output:
- Demonstration of blocklist-based rejection (Layer 0)
- Pattern-based content classification (Layer 1)
- Fallback to foundation model for edge cases (Layer 2)
"""

from spl import SPLAgent


def main():
    """Run content moderation example."""
    print("\n" + "=" * 60)
    print("SPL Framework - Content Moderation Example")
    print("=" * 60 + "\n")

    # Initialize agent with strict validation
    agent = SPLAgent(
        agent_id="content_moderator",
        confidence_threshold=0.90,  # Higher threshold for moderation
    )

    # Configure Layer 0: Add blocklist terms
    blocklist_terms = [
        "malicious_term",
        "banned_phrase",
        "prohibited_content",
    ]

    for term in blocklist_terms:
        agent.add_to_blocklist(term)

    print(f"Added {len(blocklist_terms)} terms to blocklist (Layer 0)")

    # Configure Layer 1: Add content classification patterns
    moderation_patterns = [
        ("violence", r"attack|fight|kill|harm|violent", "violence", 0.92),
        ("harassment", r"hate|harass|bully|threaten", "harassment", 0.94),
        ("profanity", r"profane_word|explicit_term", "profanity", 0.96),
        ("safe", r"hello|welcome|thanks|appreciate|help", "safe", 0.95),
        ("question", r"how to|what is|can you|please explain", "question", 0.90),
    ]

    for name, regex, category, conf in moderation_patterns:
        agent.layer1.add_pattern(name, regex, category, conf)

    print(f"Added {len(moderation_patterns)} patterns to Layer 1")
    print()

    # Sample content for moderation
    content_items = [
        {
            "user_id": "user001",
            "content": "Hello everyone! Welcome to our community.",
            "expected": "safe",
        },
        {
            "user_id": "user002",
            "content": "This contains malicious_term that should be blocked.",
            "expected": "blocked",
        },
        {
            "user_id": "user003",
            "content": "How to learn programming? Please explain the basics.",
            "expected": "question",
        },
        {
            "user_id": "user004",
            "content": "I appreciate your help with my project. Thanks!",
            "expected": "safe",
        },
        {
            "user_id": "user005",
            "content": "This is a general message without any triggers.",
            "expected": "other",
        },
        {
            "user_id": "user006",
            "content": "The banned_phrase appears in this content.",
            "expected": "blocked",
        },
        {
            "user_id": "user007",
            "content": "What is the weather like today? Can you help?",
            "expected": "question",
        },
        {
            "user_id": "user008",
            "content": "Thanks for the welcome! I appreciate the community.",
            "expected": "safe",
        },
    ]

    print(f"Moderating {len(content_items)} content items...")
    print("-" * 60)
    print()

    # Process content
    stats = {"blocked": 0, "approved": 0, "by_layer": {0: 0, 1: 0, 2: 0}}

    for i, item in enumerate(content_items, 1):
        request = {"user_id": item["user_id"], "content": item["content"]}

        result = agent.process(request)

        # Track statistics
        stats["by_layer"][result.layer] += 1
        if result.category == "REJECTED":
            stats["blocked"] += 1
            status = "🚫 BLOCKED"
        else:
            stats["approved"] += 1
            status = "✅ APPROVED"

        layer_name = ["Reactive", "Tactical", "Deliberative"][result.layer]
        expected_match = (
            "✓"
            if (item["expected"] == "blocked" and result.category == "REJECTED")
            or (item["expected"] != "blocked" and result.category != "REJECTED")
            else "?"
        )

        print(f"Content {i}: {item['content'][:45]:<45}...")
        print(f"  Status: {status:<15} | Category: {result.category}")
        print(f"  Layer: {layer_name:<12} | Method: {result.method}")
        print(f"  Confidence: {result.confidence:.2f}    | Expected: {expected_match}")
        print()

    # Summary
    print("-" * 60)
    print("\nModeration Summary")
    print("-" * 60)

    print(f"\nTotal items processed: {len(content_items)}")
    print(f"Blocked: {stats['blocked']} ({stats['blocked']/len(content_items)*100:.1f}%)")
    print(f"Approved: {stats['approved']} ({stats['approved']/len(content_items)*100:.1f}%)")

    print("\nLayer breakdown:")
    for layer, count in stats["by_layer"].items():
        layer_name = ["Reactive (Blocklist)", "Tactical (Patterns)", "Deliberative (FM)"][
            layer
        ]
        print(f"  Layer {layer} ({layer_name}): {count} items")

    report = agent.report()
    print(f"\nCost analysis:")
    print(f"  Total cost: ${report['total_cost']:.4f}")
    print(f"  Suppression rate: {report['suppression_rate']:.1%}")

    print()
    print("=" * 60)
    print("Content moderation example complete!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
