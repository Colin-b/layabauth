from http import HTTPStatus

from flask import make_response
from werkzeug.wrappers import BaseResponse


def dataframe_as_json_response(df, code: HTTPStatus = HTTPStatus.OK, date_unit: str = 'ms') -> BaseResponse:
    """
    Generate a Flask response with Pandas Dataframe

    :param df: Dataframe to send back to the client
    :param code: Reply HTTP Status code
    :param date_unit: The time unit to encode to, governs timestamp and ISO8601 precision. One of ‘s’, ‘ms’, ‘us’, ‘ns’ for second, millisecond, microsecond, and nanosecond respectively.
    :return: Flask response with serialized form of Dataframe and HTTP Status 200
    """
    response = make_response(df.to_json(orient='records', date_format='iso', date_unit=date_unit), code)
    response.headers['Content-Type'] = 'application/json'
    return response
