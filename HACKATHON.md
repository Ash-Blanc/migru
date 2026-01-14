# Migru x Med-Gemma Impact Challenge

**Migru** has been upgraded to participate in the **Kaggle Med-Gemma Impact Challenge**, focusing on leveraging Google's **Gemma 2** (as the foundation for Med-Gemma applications) to build a human-centered, privacy-first AI companion for chronic migraine sufferers.

## 🎯 Challenge Alignment

This project addresses the challenge goal of "Building Human-Centered AI Applications" by providing a supportive, evidence-based companion for managing chronic pain conditions.

### Key Features

1.  **Med-Gemma Powered Insights**:
    *   Utilizes **Gemma 2 (9B)** (via local inference) as the core intelligence for the `Med-Gemma Insight` agent.
    *   Implements **HAI-DEF (Health AI Developer Foundations)** principles: Helpful, Harmless, Honest.
    *   Provides clinical context and safety assessments (red flag detection) for reported symptoms.

2.  **Edge AI & Privacy**:
    *   Runs entirely **locally** (on-device) to ensure sensitive health data never leaves the user's machine.
    *   Aligns with the need for secure, private healthcare applications.

3.  **Human-Centered Design**:
    *   **Empathy First**: The "Companion" mode prioritizes validation and emotional support, acknowledging the psychological burden of chronic pain.
    *   **Actionable Advice**: The "Advisor" mode bridges the gap between medical knowledge and daily lifestyle choices.

## 🏗️ Architecture

-   **Model**: Google Gemma 2 (9B Instruction Tuned) acting as the local "Med-Gemma" proxy.
-   **Framework**: Agno AI for agent orchestration.
-   **Interface**: Terminal-based UI (Rich) for low-latency, distraction-free interaction.

## 🚀 How to Run (Med-Gemma Mode)

1.  **Ensure Local Model is Ready**:
    ```bash
    ollama pull gemma2:9b
    ```

2.  **Run Migru**:
    ```bash
    uv run -m app.main
    ```

3.  **Access Medical Insights**:
    *   Simply ask about symptoms using clinical terms (e.g., "Analyze my aura symptoms").
    *   Or use the `/med` command (coming soon) or type "medical analysis" to trigger the Med-Gemma agent.

## ⚠️ Disclaimer

Migru is a supportive tool, not a medical device. It does not provide diagnosis or treatment. Always consult a healthcare professional.
