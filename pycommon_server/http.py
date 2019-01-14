import io
from http import HTTPStatus

import pandas as pd
from flask import make_response


def dataframe_200(df):
    """
    Generate a Flask response with Pandas Dataframe

    :param df: Dataframe to send back to the client
    :return: Flask response with serialized form of Dataframe and HTTP Status 200
    """
    response = make_response(df.to_json(orient='records', date_format='iso'), HTTPStatus.OK)
    response.headers['Content-Type'] = 'application/json'
    return response


def dataframe_as_excel_200(df, file_name='sheet.xlsx', sheet_name='Sheet1', writer_callback=None):
    """
    Generate a Flask response with Pandas Dataframe to Excel sheet

    :param df: Dataframe to send back to the client as an Excel Sheet
    :param sheet_name: Excel sheet name
    :param writer_callback: callback to apply user specifics to Excel Writer
    :return: Flask response with serialized form of Dataframe as Excel and HTTP Status 200
    """
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    if writer_callback:
        writer_callback(writer)
    writer.close()
    resp = make_response(out.getvalue(), HTTPStatus.OK)
    resp.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    resp.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return resp
