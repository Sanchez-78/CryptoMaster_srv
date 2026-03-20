def compute_position_size(confidence, balance=1000):
    base_risk = 0.01

    risk = base_risk * (0.5 + confidence)

    size = balance * risk

    return round(size, 2)