<task>
Implement prediction model for crypto signals.
</task>

<requirements>
- manual logistic regression (no sklearn)
- input: feature dict
- output:
  - probability (0–1)
  - signal: BUY / SELL / HOLD

<logic>
- if prob > 0.6 → BUY
- if prob < 0.4 → SELL
- else HOLD
</logic>

<persistence>
- store weights in Firebase
- load weights on start
</persistence>

<constraints>
- keep it simple
- no overengineering
</constraints>

<output>
- src/services/model.py
</output>




