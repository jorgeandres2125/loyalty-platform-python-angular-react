"""Pytest config compartido.

Sin fixtures asincrónicas globales: cada test que necesite cliente HTTP
usa `fastapi.testclient.TestClient` directamente (gestiona lifespan ok).
"""
