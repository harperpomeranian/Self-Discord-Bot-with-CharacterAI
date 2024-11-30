from characterai import sendCode, authUser

def main():
    email = input('C.AI YOUR EMAIL: ')
    sendCode(email)
    link = input('Login link from email (Do NOT click the link): ')
    token = authUser(link, email)

    print(f'YOUR TOKEN: {token}')

if __name__ == "__main__":
    main()