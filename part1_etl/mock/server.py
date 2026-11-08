from http.server import ThreadingHTTPServer

import mock_erp_2

if __name__ == "__main__":
    # The mock binds to 127.0.0.1, unreachable from other containers: same Handler, on 0.0.0.0.
    print(f"ERP mock (original) listening on 0.0.0.0:{mock_erp_2.PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", mock_erp_2.PORT), mock_erp_2.Handler).serve_forever()
