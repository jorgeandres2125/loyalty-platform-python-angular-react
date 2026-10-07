from enum import StrEnum


class AlgoritmoFirma(StrEnum):
    """AP-0006: algoritmos de firma digital aprobados (asimetricos, con no repudio).

    El MVP usa ES256 (ECDSA P-256 con SHA-256), estandar JWS y ligero. ES384 y EDDSA
    (Ed25519) quedan declarados para casos de mayor valor o interoperabilidad. Quedan
    PROHIBIDOS por politica los simetricos (HS256) y los debiles (MD5, SHA-1, none):
    no aportan no repudio.
    """

    ES256 = "ES256"
    ES384 = "ES384"
    EDDSA = "EdDSA"
