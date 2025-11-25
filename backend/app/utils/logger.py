# esta funcion nos sirve para imprimir en consola el mensaje y el payload
def log(message: str, payload=None):
    print(f"[LOG] {message}")
    if payload:
        print(payload)
