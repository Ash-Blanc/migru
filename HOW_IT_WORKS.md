# 🧠 How Migru Works: End-to-End Architecture

Migru is designed as a **local-first**, reactive, and adaptive system. It moves beyond simple request-response loops by integrating real-time analytics and data fusion.

## 🔄 System Overview

The system operates in three parallel layers:

1.  **Interaction Layer (CLI)**: Handles user input, rendering, and immediate feedback.
2.  **Intelligence Layer (Agents)**: Dynamic AI models (Fast/Smart) that generate wisdom and empathy.
3.  **Analytics Layer (Pathway)**: A streaming engine that fuses conversation data with biometric signals to trigger reactive alerts.

---

## 🏗️ The Pathway Integration (Analytics Layer)

The core of Migru's "awareness" is powered by **Pathway**, a high-throughput streaming framework. It allows the system to detect patterns *as they happen*, rather than analyzing old logs.

### 1. Data Ingestion (Redis Streams)
The CLI injects two types of events into local Redis Streams:
-   `wellness_stream`: Every user message, labeled with intent (e.g., "symptom", "relief").
-   `biometric_stream`: Sensor data (Heart Rate, Sleep Score) simulated via `/bio`.

### 2. Data Fusion (Temporal Join)
Pathway "fuses" these streams by joining them over a sliding time window (e.g., 5 minutes).
*   **Goal**: Correlate *what you feel* with *what your body is doing*.
*   **Logic**: "Find biometric events that occurred ±5 minutes around a verbal symptom report."

```python
# Simplified Pathway Logic
fused_data = wellness_stream.windowby(
    time_window
).join(
    biometric_stream.windowby(time_window),
    on="user_id"
)
```

### 3. Reactive Alerting
Once data is fused, Pathway filters for critical patterns:
*   **Trigger**: Symptom report + High Heart Rate (>100 bpm).
*   **Action**: Write a high-priority alert to the `migru_alerts` Redis stream.

This allows the main agent to interrupt or adapt its persona immediately when it detects high physiological stress.

---

## ⚡ Dynamic Routing (Intelligence Layer)

To balance speed and depth, Migru uses a **Dynamic Router**:

1.  **Input Analysis**: Heuristics analyze message complexity (word count, keywords like "why" or "how").
2.  **Model Selection**:
    *   **Fast Path (< 15 words)**: Routes to `Cerebras (Llama 3.1 8b)` for sub-second conversational flow.
    *   **Smart Path (Complex)**: Routes to `Mistral Small` for deep reasoning, research, or empathy.
3.  **Context Injection**: Before generation, the **Adaptive Context Service** injects the user's current mood momentum into the system prompt.

---

## 🔄 The Feedback Loop

1.  **User types**: "I feel anxious."
2.  **CLI**: Detects mood "anxious" -> Updates State -> Displays "Thinking..."
3.  **Pathway**: Sees "anxious" + reads recent HR (110bpm) -> Triggers "High Stress Alert".
4.  **Router**: Selects Smart Model (due to emotional weight).
5.  **Agent**: Generates response using "Calm/Grounding" persona (adapted to anxiety).
6.  **Response**: "I hear that anxiety. Your heart is racing, but you are safe. Let's exhale together."

This entire loop happens in seconds, creating a companion that feels alive and aware of your whole context.
