from cryptography.fernet import Fernet

clear_pw = input("Inserire la password che si vuole criptare: ")

with open('fernet.key', 'rb') as kf:
    key = kf.readline()
    
f = Fernet(key)
encripted_password = f.encrypt(clear_pw.encode())

print(encripted_password.decode("utf-8"))