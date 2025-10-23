# Implementation Plan Template

> _How to use this file_
> Replace every [placeholder] with real content, remove the examples, and delete this note.

## 1 Overview

Briefly describe _what_ the feature is and _why_ you’re building it (2–3 sentences).

## 2 Current State Analysis

### 2.1 Existing Process Example

1. _Data Retrieval_ – [one-line description]
2. _Processing_ – [one-line description]
3. _Content Generation_ – [one-line description]
4. _Output_ – [one-line description]

### 2.2 Current Data Model Example

- _Summary_ – fields: [field1], [field2], …
- _Takeaway_ – fields: [field1], [field2], …
- _Source_ – fields: [field1], [field2], …

### 2.3 Proposed changes

- Changes to data model / process

---

## 3 Implementation Progress Tracker

Example

| Step | Area / Component                | Status | Dependencies | Ready to Close? |
| ---- | ------------------------------- | ------ | ------------ | --------------- |
| 1.1  | Folder structure: [short label] | ☐      | —            | ☐               |
| 1.2  | Database: [short label]         | ☐      | 1.1          | ☐               |
| 2.1  | Processing: [short label]       | ☐      | 1.x          | ☐               |
| 2.2  | Processing: [short label]       | ☐      | 2.1          | ☐               |
| 3.1  | Generator: [short label]        | ☐      | 2.x          | ☐               |
| 4.1  | Templates / UI: [short label]   | ☐      | 3.x          | ☐               |

(Add or delete rows as needed.)

## 4 Implementation Plan

Fill in placeholders in the block below for _every_ numbered step in the tracker (including the Testing step).

Step [X.X]: [High‑level title]

_Purpose / Scope_

- [high‑level goal]

_Requirements_

- [requirement A]
- [requirement B]

_Implementation Placeholder_

Include boilerplate code, configuration, or diagrams required to satisfy the requirements. Include these with a code block, or link to a file in the repository.

<details markdown="1">
<summary markdown="span">Collapsible code</summary>

python
print("hello world")

</details>

_Acceptance Criteria_

- [criterion 1]
- [criterion 2]

_Testing strategy_

- [unit tests]
  - [test]
- [integration tests]
  - [test]

(Repeat for Steps 1.x through 6.x, including \*_5.1 Testing_.  
For the testing step, list unit‑test targets, coverage goals, and sample boilerplate test code.)\*

## 5 Technical Standards

See the cursor rules which contain technical standards, add the rules explictly which are relevant

| Area               | Standard                                                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Code Style         | Ruff = 0 violations                                                                                               |
| Package Management | Use uv for dependency management, run Python via uv run, keep libraries pinned, audited, and isolated per project |
| Docs               | Google‑style docstrings                                                                                           |
| DB                 | Indexed columns, migration scripts                                                                                |
| Security           | [items]                                                                                                           |

## 6 Success Metrics

- _Functional_ – e.g., source attribution ≥ 95 %
- _Performance_ – e.g., generation < 30 s
- _Quality_ – e.g., user CSAT ≥ 4.5 / 5

## 7 Risk Mitigation

| Risk Type   | Description | Mitigation | Owner  |
| ----------- | ----------- | ---------- | ------ |
| Technical   | [risk]      | [action]   | [name] |
| Business    | [risk]      | [action]   | [name] |
| Integration | [risk]      | [action]   | [name] |
