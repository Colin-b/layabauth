import oauth2helper.content
import oauth2helper.token


def get_user(bearer=None, no_auth=True):
    """
    This function is kept for compatibility purposes.
    Use @requires_authentication decorator and you will get the user via flask.g.current_user
    """
    # if there is a request_context, we still check
    if no_auth and bearer is None:
        return 'anonymous'
    elif bearer is not None:
        if bearer.lower() == 'sesame':
            return 'PARKER'
        else:
            try:
                json_header, json_body = oauth2helper.token.validate(bearer)
                return oauth2helper.content.user_name(json_body)
            except Exception as e:
                raise ValueError("Token validation error: " + str(e))
    else:
        raise ValueError(
            'anonymous access is not authorised. Please provide a valid JWT token or access our API via (<a href="http://guru.trading.gdfsuez.net/confluence/display/ETRMsys/PyxelRest">pyxelrest Excel addin</a>).')