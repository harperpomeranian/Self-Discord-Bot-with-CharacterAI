from characterai import sendCode, authUser

def main():
    email = input('YOUR EMAIL: ')
    sendCode(email)
    link = input('LOGIN LINK IN MAIL: ')
    token = authUser(link, email)

    print(f'YOUR TOKEN: {token}')

if __name__ == "__main__":
    main()