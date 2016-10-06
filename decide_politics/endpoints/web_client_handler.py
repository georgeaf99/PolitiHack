from decide_politics.flask import app

import jsonpickle
from flask import request

import decide_politics.logic.messaging as messaging
import shared.common as common
from decide_politics.core.models import Customer


@app.route('/web/handle_message/<customer_uuid>', methods=["POST"])
@common.enforce_request_json_schema(dict(
    message_body=str
))
def handle_message(customer_uuid):
    """Handles messages from a phone number with body

    @param customer_uuid The UUID of the sender

    @data message_body The body of the message
    """

    data = jsonpickle.decode(request.data.decode("utf-8"))
    message_body = data["message_body"]

    # Retrieve the message and create the customer
    customer = Customer.load_from_db(customer_uuid)
    messaging.on_message_recieve(customer, message_body)

    return jsonpickle.encode(dict(
        success=True
    ))
