# SPL Architecture Guide

This document provides a deep dive into the 3-layer behavior-based architecture of the Subsumption Pattern Learning (SPL) framework.

## Overview

SPL implements a hierarchical decision system where lower layers can **suppress** upper layers, preventing expensive foundation model calls before they occur.

## Layer Architecture

### Layer 0: Reactive Schemas (Validation)

- **Cost:** $0
- **Speed:** <1ms
- **Purpose:** Fast, deterministic validation

### Layer 1: Tactical Behaviors (Pattern Matching)

- **Cost:** $0.001 per match
- **Speed:** <10ms
- **Purpose:** Match against learned patterns before foundation model

### Layer 2: Deliberative (Foundation Model Reasoning)

- **Cost:** $0.01+ per call
- **Speed:** 100-500ms
- **Purpose:** Complex reasoning for novel situations

## Design Principles

Based on Ronald Arkin's behavior-based robotics and Rodney Brooks' subsumption architecture.

---

*For more details, see the main [README.md](../README.md).*
