from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64


class Encryption(object):
    def __init__(self):
        # 伪随机数生成器
        self.random_generator = Random.new().read

    def getKey(self):
        # rsa算法生成实例
        rsa = RSA.generate(1024, self.random_generator)
        # master的秘钥对的生成
        private_pem = rsa.exportKey()
        public_pem = rsa.publickey().exportKey()
        key = {}
        key["private"] = private_pem
        key["public"] = public_pem
        return key

    def rsa_long_encrypt(self, msg, pub_key_str, length=100):
        """
        单次加密串的长度最大为 (key_size/8)-11
        1024bit的证书用100， 2048bit的证书用 200
        """
        pubobj = RSA.importKey(pub_key_str)
        pubobj = Cipher_pkcs1_v1_5.new(pubobj)
        res = []
        for i in range(0, len(msg), length):
            res.append(
                str(
                    base64.b64encode(pubobj.encrypt(
                        msg[i:i + length].encode(encoding="utf-8"))), 'utf-8'
                )
            )
        return "".join(res)

    def rsa_long_decrypt(self, msg, priv_key_str, length=172):
        """
        1024bit的证书用128，2048bit证书用256位
        """
        privobj = RSA.importKey(priv_key_str)
        privobj = Cipher_pkcs1_v1_5.new(privobj)
        res = []
        for i in range(0, len(msg), length):
            res.append(
                str(
                    privobj.decrypt(
                        base64.b64decode(msg[i:i + length])
                        , 'xyz'), 'utf-8'
                )
            )
        return "".join(res)


if __name__ == '__main__':
    str1 = """
    {'xdata': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59], 'ydata': [107, 110, 106, 104, 112, 104, 109, 106, 99, 119, 105, 108, 119, 82, 87, 93, 94, 107, 106, 84, 87, 114, 101, 80, 102, 87, 103, 87, 99, 104, 119, 84, 120, 107, 115, 84, 109, 85, 84, 98, 113, 85, 81, 80, 88, 96, 109, 119, 115, 84, 106, 87, 98, 114, 92, 90, 89, 83, 92, 91], 'age': 20.0, 'gender': 1.0, 'OCC': 1.0, 'MHR': 40.0}
    """
    a = Encryption()
    key = a.getKey()
    prikey = key['private'].decode()
    pubkey = key['public'].decode()
    print(prikey)
    print(pubkey)
    print(str1)
    cipher_text = a.rsa_long_encrypt(str1, pubkey)
    print(cipher_text)
    plaintext = a.rsa_long_decrypt(cipher_text, prikey)
    print(plaintext)
