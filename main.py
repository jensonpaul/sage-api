from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from decouple import config, UndefinedValueError
from db import SageERP
from datetime import datetime

app = FastAPI()


def is_allowed(host_ip) -> bool:
    """
    Check if the host ip is allowed to access the resource based on ALLOWD_IPS environment variable

    :param host_ip: The host ip address
    :return: True if the host ip is allowed, False otherwise
    """
    try:
        ip_addresses = config('ALLOWED_IPS', default='')

        if ip_addresses == '':
            return True

        allowd_ips = ip_addresses.split(',')
        return host_ip in allowd_ips
    except UndefinedValueError as err:
        print(f'Error which checking allowd IPs: {err}')
        return False


@app.middleware("http")
async def before_request(request: Request, call_next):
    """
    Middleware to check if the host ip is allowed to access the resource
    """
    try:
        method = request.method
        path = request.url.path
        # print(f"method: {method}, path: {path}")
        ip_addr = str(request.client.host)
        if not is_allowed(ip_addr):
            data = {"message": f"IP {ip_addr} is not allowed to access this resource"}
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
        response = await call_next(request)
    finally:
        pass
    return response


@app.get("/SageErpUsers")
async def get_sage_erp_users():
    """
    Get the list of Sage ERP users
    """
    try:
        sdb = SageERP()
        users = sdb.get_sage_erp_users()

        appusers = sdb.appusers
        biusers = sdb.biusers

        data = {"users": users, "message": "Success",
                "appusers": appusers, "biusers": biusers}
    except Exception as err:
        print(f'Unexpected error: {err}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Unexpected Error: {err}"})
    return data


if __name__ == "__main__":
    import uvicorn
    from decouple import config

    ip = config('IP', default='localhost')
    port = config('PORT', default=8001, cast=int)

    uvicorn.run(app, host=ip, port=port)
