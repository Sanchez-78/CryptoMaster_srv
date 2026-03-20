<task>
Implement evaluation and learning system.
</task>

<requirements>
- load past signals from Firebase
- evaluate only signals older than EVAL_DELAY_HOURS
- fetch actual price from Binance for evaluation

<evaluation>
- BUY = profit if price increased
- SELL = profit if price decreased
- HOLD = neutral
</evaluation>

<learning>
- adjust weights based on outcome:
  - correct prediction → reinforce weights
  - wrong prediction → penalize weights
- simple gradient-like update (no ML libraries)
</learning>

<constraints>
- keep it simple
- no overengineering
</constraints>

<output>
- src/services/evaluator.py
</output>
