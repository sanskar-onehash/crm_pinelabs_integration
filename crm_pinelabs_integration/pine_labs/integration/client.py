import requests

from crm_pinelabs_integration.pine_labs.integration import auth


def prepare_headers(headers=None):
    if not headers:
        headers = {"Content-Type": "application/json"}
    return headers


def prepare_url(endpoint):
    return auth.get_base_uri() + endpoint


def make_get_request(
    endpoint,
    headers=None,
    params=None,
    data=None,
    json=None,
    parse_as_json=True,
):
    headers = prepare_headers(headers)

    res = requests.get(
        prepare_url(endpoint),
        headers=headers,
        params=params,
        data=data,
        json=json,
    )
    res.raise_for_status()

    if parse_as_json:
        return res.json()
    return res.text


def make_post_request(
    endpoint,
    headers=None,
    params=None,
    data=None,
    json=None,
    parse_as_json=True,
):
    headers = prepare_headers(headers)

    res = requests.post(
        prepare_url(endpoint),
        headers=headers,
        params=params,
        data=data,
        json=json,
    )
    res.raise_for_status()

    if parse_as_json:
        return res.json()
    return res.text


def make_patch_request(
    endpoint,
    headers=None,
    params=None,
    data=None,
    json=None,
    parse_as_json=True,
):
    headers = prepare_headers(headers)

    res = requests.patch(
        prepare_url(endpoint),
        headers=headers,
        params=params,
        data=data,
        json=json,
    )
    res.raise_for_status()

    if parse_as_json:
        return res.json()
    return res.text


def make_delete_request(
    endpoint,
    headers=None,
    params=None,
    data=None,
    json=None,
    parse_as_json=True,
):
    headers = prepare_headers(headers)

    res = requests.delete(
        prepare_url(endpoint),
        headers=headers,
        params=params,
        data=data,
        json=json,
    )
    res.raise_for_status()

    if parse_as_json:
        return res.json()
    return res.text
