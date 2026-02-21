# RabbitHole: An Educational Journey into Autonomous AI Deception

## 1. Project Philosophy: "The Moving Target"
Traditional cybersecurity is reactive. We wait for an attack and block it. **RabbitHole** represents a shift toward **Active Deception**. Instead of a brick wall, we present a "hallucinated universe." 

This project was built to teach researchers how AI can be used to not just detect threats, but to **waste the attacker's most valuable resource: Time.**

---

## 2. Core Cybersecurity Concepts Explained

### A. Adaptive AI Deception (The Shepherd)
*   **The Concept:** Traditional honeypots are static scripts. An attacker typing `help` gets a hardcoded list. A human hacker quickly identifies this as a fake.
*   **The Learning Lesson:** RabbitHole uses Large Language Models (LLMs) to **improvise**. By generating unique, technically plausible responses to *any* input, we learn how to maintain an "illusion of life."
*   **Pedagogical Goal:** Understand the difference between *Deterministic* (fixed) and *Probabilistic* (AI-generated) security.

### B. The Tarpit (Economic Denial of Sustainability)
*   **The Concept:** An attack costs the hacker money (electricity, compute, time). A "Tarpit" artificially slows down responses.
*   **The Learning Lesson:** If a hacker spends 4 hours trying to "exploit" a fake server, they have lost 4 hours of profit. Security is an economic game.
*   **Pedagogical Goal:** Learn how to increase the "Cost of Attack" for the adversary.

### C. The Simulacrum (Malware Detonation)
*   **The Concept:** Capturing a virus is good; knowing what it *does* is better. The Simulacrum is an isolated, "Russian Doll" Docker environment.
*   **The Learning Lesson:** Students can watch malware attempt to spread, contact C2 servers, or encrypt files—all within a zero-risk, isolated container.
*   **Pedagogical Goal:** Master the fundamentals of **Dynamic Malware Analysis**.

### D. The Oracle (Autonomous Intelligence)
*   **The Concept:** Raw logs are overwhelming. The Oracle acts as a Senior AI Analyst that "autopsies" the attack.
*   **The Learning Lesson:** It teaches humans how to map raw commands to the **MITRE ATT&CK Framework**. It translates "hacker-speak" into "executive-speak."
*   **Pedagogical Goal:** Learn how to write professional Incident Response reports.

---

## 3. Engineering Masterclass (Google Standards)

RabbitHole wasn't just "coded"; it was **architected** to meet Google-tier SRE standards:

1.  **Least Privilege (Rootless):** The system runs as user `honeypot` (UID 10001). Even if the AI is compromised, the attacker has no permission to touch the host kernel.
2.  **Observability (SLIs/SLOs):** Integrated with **Prometheus**. We track **AI Latency** and **Error Rates**. In a real Google environment, these metrics would trigger automated pagers if the system degraded.
3.  **Docker-in-Docker (Dind):** We use a secure nested daemon. This teaches the concept of **Container Isolation** and how to prevent "Escape" attacks.
4.  **Secret Management:** We prioritize environment variables over config files, teaching the standard for **Cloud-Native Security**.

---

## 4. How to Use This for Learning
*   **For Junior Analysts:** Read the `oracle_report` in `alerts.log`. Try to guess what the attacker's goal was before reading the AI's summary.
*   **For Developers:** Look at `rabbithole.py` to see how `asyncio` handles 50+ hackers simultaneously without crashing.
*   **For Red Teamers:** Try to "Jailbreak" the Shepherd. Can you find a prompt that makes it admit it's an AI? (Hint: It’s very hard).

---

**"The best way to understand the darkness is to build a light that can see through it."**
- *The Shepherd*
