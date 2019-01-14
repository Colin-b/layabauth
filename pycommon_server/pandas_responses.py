from http import HTTPStatus

from flask import make_response
from werkzeug.wrappers import BaseResponse


def dataframe_as_response(df, code: HTTPStatus = HTTPStatus.OK) -> BaseResponse:
    """
    Generate a Flask response with Pandas Dataframe

    :param df: Dataframe to send back to the client
    :param code: Reply HTTP Status code
    :return: Flask response with serialized form of Dataframe and HTTP Status 200
    """
    response = make_response(df.to_json(orient='records', date_format='iso'), code)
    response.headers['Content-Type'] = 'application/json'
    return response
