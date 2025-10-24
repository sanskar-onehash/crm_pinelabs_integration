from crm_pinelabs_integration.pine_labs.integration import client


def create_order(order_payload):
    return client.make_post_request(
        "/UploadBilledTransaction",
        json=order_payload,
        parse_as_json=True,
    )


def get_order_status(order_payload):
    return client.make_post_request(
        "/GetCloudBasedTxnStatus",
        json=order_payload,
        parse_as_json=True,
    )


def cancel_order(order_payload):
    return client.make_post_request(
        "/CancelTransaction",
        json=order_payload,
        parse_as_json=True,
    )
