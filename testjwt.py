import jwt

SECRET = 'rqtyfwdvjsabfhegwfybcabcyabejbdjcbuewcbkjkab'

def generate_token():
    data = {
        "user": 'Muhamad Sechan Syadat',
        "result": True
    }
    return jwt.encode(data, "muhamad sechan syadat")

def validate_token(token):
    try:
        return jwt.decode(token, SECRET)
    except Exception as error:
        return False

def main():
    token = generate_token()

    is_valid = validate_token(token)

    print('Token is valid', is_valid)

main()
