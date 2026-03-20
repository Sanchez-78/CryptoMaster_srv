import stripe

stripe.api_key = "YOUR_SECRET_KEY"


def create_checkout_session(price_id, user_id):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        success_url="https://yourapp.com/success",
        cancel_url="https://yourapp.com/cancel",
        metadata={
            "user_id": user_id
        }
    )
    return session.url