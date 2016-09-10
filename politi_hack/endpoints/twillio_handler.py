from politi_hack.flask import app

from flask import request

from politi_hack.core.models import Customer
import politi_hack.logic.messaging as messaging


@app.route('/sms/handle_sms', methods=["POST"])
def handle_sms():
    """Handles Twillio SMS message"""
    customer_phone_number = request.values["From"]
    text_message_body = request.values["Body"]

    # Retrieve the customer from the DB or create a new one
    customer = Customer.get_customer_by_phone_number(customer_phone_number)
    if not customer:
        customer = Customer.create_new({
            CFields.PHONE_NUMBER: customer_phone_number,
        })

        # Save the customer to the DB
        customer.create()

    messaging.on_message_recieve(customer, text_message_body)
