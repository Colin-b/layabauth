import datetime
import re


def _pycommon_status(health_response):
    if isinstance(health_response, dict):
        return health_response.get("status", "pass")
    return "pass"


def http_details(
    service_name: str,
    url: str,
    status_extracting: callable = None,
    failure_status: str = "fail",
    **requests_args,
) -> (str, dict):
    """
    Return Health details for an external service connection.

    :param service_name: External service name.
    :param url: External service health check URL.
    :param status_extracting: Function returning status according to the JSON response (as parameter).
    Default to the way status should be extracted from a python_service_template based service.
    :param failure_status: Status to return in case of failure (Exception or HTTP rejection). fail by default.
    :return: A tuple with a string providing the status (pass, warn, fail) and the details.
    Details are based on https://inadarei.github.io/rfc-healthcheck/
    """
    import requests

    try:
        response = requests.get(
            url, timeout=requests_args.pop("timeout", (1, 5)), **requests_args
        )
        if response:
            if not status_extracting:
                status_extracting = _pycommon_status

            response = (
                response.json()
                if re.match(
                    "application/(health\+)?json", response.headers["Content-Type"]
                )
                else response.text
            )
            return (
                status_extracting(response),
                {
                    f"{service_name}:health": {
                        "componentType": url,
                        "observedValue": response,
                        "status": status_extracting(response),
                        "time": datetime.datetime.utcnow().isoformat(),
                    }
                },
            )
        return (
            failure_status,
            {
                f"{service_name}:health": {
                    "componentType": url,
                    "status": failure_status,
                    "time": datetime.datetime.utcnow().isoformat(),
                    "output": response.text,
                }
            },
        )
    except Exception as e:
        return (
            failure_status,
            {
                f"{service_name}:health": {
                    "componentType": url,
                    "status": failure_status,
                    "time": datetime.datetime.utcnow().isoformat(),
                    "output": str(e),
                }
            },
        )


def status(*statuses: str) -> str:
    """
    Return status according to statuses:
    fail if there is at least one fail status, warn if there is at least one warn status
    pass otherwise

    :param statuses: List of statuses, valid values are pass, warn or fail
    :return: Status according to statuses
    """
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"
