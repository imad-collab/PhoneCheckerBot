import httpx

# Save original __init__
orig_init = httpx.AsyncClient.__init__

def ipv4_init(self, *args, **kwargs):
    kwargs["transport"] = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    return orig_init(self, *args, **kwargs)

httpx.AsyncClient.__init__ = ipv4_init


