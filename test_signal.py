import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot1.market_provider import MarketProvider
from src.services.ml_model import MLModel

def run_test():
    print("Initializing Market Provider...")
    provider = MarketProvider()
    print("Fetching features...")
    features = provider.get_features("BTCUSDT")
    
    print("\nCalculated Features:")
    for k, v in features.items():
        print(f"  {k}: {v}")
        
    print("\nInitializing ML Model...")
    model = MLModel()
    print("Predicting Signal...")
    
    try:
        prediction = model.predict("BTCUSDT", features)
        print(f"\n✅ Prediction SUCCESS: {prediction}")
    except Exception as e:
        print(f"\n⚠️ Prediction Exception (Likely model not trained): {e}")

if __name__ == "__main__":
    run_test()
