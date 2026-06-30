from Crypto.Cipher import AES # ---- (*1)
from base64 import b64encode, b64decode

# 暗号化したいデータとパスワードを指定 --- (*2)
message = "自分がして欲しいと思うことを人にもするように。"
password = "xxxxxxxxxx" # 適当なパスワードを指定
mode = AES.MODE_EAX # 暗号化モードを指定
# AESではパスワードを16バイトに揃える --- (*3)
password = (password + "_" * 16).encode()[:16]

# 暗号化する --- (*4)
def encrypt(password, data):
    aes = AES.new(password, mode)
    data_cipher, tag = aes.encrypt_and_digest(data.encode())
    nonce = aes.nonce
    return b64encode(tag).decode('utf-8') + "::" + \
        b64encode(nonce).decode('utf-8') + "::" + \
        b64encode(data_cipher).decode('utf-8')

# 復号化する --- (*5)
def decrypt(password, encdata):
    # 暗号化されたデータを意味毎に区切る
    tag, nonce, data = [b64decode(s) for s in  encdata.split("::")]
    # 復号化
    aes = AES.new(password, mode, nonce=nonce)
    data = aes.decrypt_and_verify(data, tag)
    return data.decode("utf-8")

if __name__ == "__main__": # 関数を呼び出してテスト --- (*6)
    # 暗号化して表示
    enc = encrypt(password, message)
    print("暗号化:", enc)
    # 復号化して表示
    dec = decrypt(password, enc)
    print("復号化:", dec)
