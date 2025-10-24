from datetime import datetime

TRANSACTION_DATA_FIELDS_MAP = {
    "TID": "tid",
    "MID": "mid",
    "PaymentMode": "payment_mode",
    "Amount": "transaction_amount",
    "BatchNumber": "batch_number",
    "RRN": "rrn",
    "ApprovalCode": "approval_code",
    "Invoice Number": "invoice_number",
    "Card Number": "card_number",
    "IsPartialPayByPointsTxn": "is_partial_pay_by_points",
    "PartialAmountByCard": "partial_amount_by_card",
    "PartialAmountByReward": "partial_amount_by_reward",
    "Expiry Date": "expiry_date",
    "Card Type": "card_type",
    "Acquirer Id": "acquirer_id",
    "Acquirer Name": "acquirer_name",
    "Transaction Date": "transaction_date",
    "Transaction Time": "transaction_time",
    "AmountInPaisa": "transaction_amount_in_paisa",
    "OriginalAmount": "original_amount",
    "FinalAmount": "final_amount",
}


def parse_order_res(order_res):
    if order_res.get("TransactionData"):
        transaction_data = parse_transaction_data(order_res.get("TransactionData"))
        transaction_date = transaction_data.get("transaction_date")
        expiry_date = transaction_data.get("expiry_date")
        original_amount = int(transaction_data.get("original_amount") or "0")
        final_amount = int(transaction_data.get("final_amount") or "0")

        if transaction_date:
            time = transaction_data.get("transaction_time")

            transaction_data["transaction_date"] = datetime.strptime(
                f"{transaction_date}", "%d%m%Y"
            )

            if time:
                transaction_data["transaction_time"] = datetime.strptime(
                    f"{transaction_date} {time}",
                    "%d%m%Y %H%M%S",
                )

        if expiry_date and "X" not in expiry_date:
            transaction_data["expiry_date"] = datetime.strptime(
                f"{expiry_date}", "%d%m%Y"
            )
        else:
            transaction_data["expiry_date"] = None

        if original_amount:
            transaction_data["original_amount"] = original_amount / 100

        if final_amount:
            transaction_data["final_amount"] = final_amount / 100

        order_res["TransactionData"] = transaction_data
    return order_res


def parse_transaction_data(transaction_data):
    parsed_data = {}
    for tag_value in transaction_data:
        parsed_data[TRANSACTION_DATA_FIELDS_MAP.get(tag_value.get("Tag"))] = (
            tag_value.get("Value")
        )
    return parsed_data
