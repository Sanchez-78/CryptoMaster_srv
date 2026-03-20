def execute_trade(symbol, signal, size, price, sl, tp):
    print("\n🚀 EXECUTING TRADE")

    print(f"Symbol: {symbol}")
    print(f"Side: {signal}")
    print(f"Size: {size}")
    print(f"Entry: {price}")
    print(f"SL: {sl}")
    print(f"TP: {tp}")

    # 🔥 ZATÍM PAPER TRADING
    return {
        "status": "filled",
        "entry": price
    }