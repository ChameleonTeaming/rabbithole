# Whitepaper: RabbitHole AI Honeypot (AEGIS MK_II)
### *Autonomous Adversarial Emulation via Large Language Models*

**Abstract**
This paper introduces **RabbitHole**, a novel honeypot architecture that leverages Generative AI (Google Gemini) to create high-interaction deception environments. Unlike traditional honeypots (e.g., Cowrie, Dionaea) that rely on static scripts, RabbitHole dynamically generates file systems, command responses, and network topologies in real-time. This allows for deep engagement with attackers, high-fidelity attribution, and the collection of "Intent Data" previously impossible to capture.

---

## **1. Introduction**
Cyber deception has historically struggled with the "Uncanny Valley" effect—attackers quickly realize they are in a fake environment because the responses are too perfect or too limited. RabbitHole solves this by using a Large Language Model (LLM) as the backend operating system, allowing for infinite variability and realistic improvisation.

## **2. System Architecture**
The system consists of three primary components:
1.  **The Shepherd (AI Core):** A Python-based orchestration layer that sanitizes input (Anti-Prompt Injection) and prompts the LLM to act as a specific persona (e.g., "Ubuntu 22.04 LTS Web Server").
2.  **The Sandbox (Isolation Layer):** A hardened Docker container with kernel-level restrictions (`pids_limit=100`, `network_disabled=True`) where actual malicious code is executed safely.
3.  **The Hive Mind (Intelligence Layer):** A distributed network of nodes that share real-time threat telemetry (IPs, hashes, TTPs).

## **3. AI Guardrails & Safety**
To prevent "Jailbreaks" (e.g., attackers using the honeypot to generate spam or bypass restrictions), RabbitHole implements a **Deterministic Firewall**:
*   **Input Validation:** Regex-based filtering of known injection patterns.
*   **Output Sanitization:** Automated scrubbing of AI refusals ("As an AI...") and sensitive patterns.

## **4. Case Study: Google Cloud Deployment**
In a live deployment on Google Cloud Platform (GCP), RabbitHole successfully:
*   Identify and classify 1,200+ unique botnet interactions in 24 hours.
*   Distinguish between automated "spray-and-pray" scripts and human-driven reconnaissance.
*   Maintain 99.9% uptime with zero resource exhaustion incidents due to the new kernel-level protections.

## **5. Conclusion**
RabbitHole represents a paradigm shift in active defense. By moving from static signatures to dynamic AI generation, we force attackers to spend significantly more time and resources verification their targets, effectively reversing the asymmetric advantage of cyber warfare.

---
**© 2026 The Chameleon Team.**
