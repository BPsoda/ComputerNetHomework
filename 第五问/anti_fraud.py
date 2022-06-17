import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA, SHA256
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
 
def generate_keypair():
    '''
    generate keypair with rsa.
    '''
    rsa = RSA.generate(2048)
    # 生成私钥
    private_key = rsa.exportKey()
    print(private_key.decode('utf-8'))
    # 生成公钥
    public_key = rsa.publickey().exportKey()
    print(public_key.decode('utf-8'))

    with open('rsa_private_key.pem', 'wb')as f:
        f.write(private_key)
        
    with open('rsa_public_key.pem', 'wb')as f:
        f.write(public_key)

    return private_key, public_key

def sign(private_key, data):
    '''
    generate signature of the data with private key.
    '''
    private_key = RSA.importKey(private_key)
    signer = PKCS1_signature.new(private_key)
    digest = SHA.new()
    digest.update(data.encode("utf8"))
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    signature = signature.decode('utf-8')
    return signature

def check_sign(public_key, data, sign):
    public_key = RSA.importKey(public_key)
    verifier = PKCS1_signature.new(public_key)
    digest = SHA.new()
    digest.update(data.encode("utf8"))
    return verifier.verify(digest, base64.b64decode(sign))

def generate_msg_id(msg):
    h = SHA256.new()
    h.update(msg.encode('utf8'))
    return h.hexdigest()

def check_msg_id(id, msg):
    h = generate_msg_id(msg)
    return h == id

if __name__ == '__main__':
    prv, pub = generate_keypair()
    msg = 'hello world!'
    fraud = '你好！'
    signature = sign(prv, msg)
    print(check_sign(pub, msg, signature))
    print(check_sign(pub, fraud, signature))

    id = generate_msg_id(msg)
    print(check_msg_id(id, msg))
    print(check_msg_id(id, fraud))
