import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

AES_KEY = 'xxxx'
AES_IV = 'xxxx'
SHA256_SALT = 'xxxx'
DEFAULT_ENCODING = 'utf-8'

def sha256_encrypt(text):
  return sha256_encrypt_(text, SHA256_SALT)

def sha256_encrypt_(text, salt):
  # 创建SHA-256哈希对象
  hash_object = hashlib.sha256((text + salt).encode(DEFAULT_ENCODING))
  # 获取加密后的密码字符串
  encrypted = hash_object.hexdigest()
  return encrypted

# 加密
def aes_encrypt(text):
	return aes_encrypt_(AES_KEY, AES_IV, text)
# 解密
def aes_decrypt(text): 
  return aes_decrypt_(AES_KEY, AES_IV, text)

# 加密
def aes_encrypt_(key, iv, text):
	# 使用key,选择加密方式
  cryptor = AES.new(key.encode(DEFAULT_ENCODING), AES.MODE_CBC, iv.encode(DEFAULT_ENCODING))
	# 使用pkcs7补全
  pad_pkcs7 = pad(text.encode(DEFAULT_ENCODING), AES.block_size, style='pkcs7')
  ciphertext = cryptor.encrypt(pad_pkcs7)
  # 加密结果
  ciphertext = base64.encodebytes(ciphertext).decode(DEFAULT_ENCODING).strip()
  return ciphertext
# 解密
def aes_decrypt_(key, iv, text): 
  cryptor = AES.new(key.encode(DEFAULT_ENCODING), AES.MODE_CBC, iv.encode(DEFAULT_ENCODING))
  # 对传入的text转换为字节码
  text = base64.decodebytes(text.encode(DEFAULT_ENCODING))
	# 对解密结果转换为字符串
  plain_text = cryptor.decrypt(text)
  plain_text = unpad(plain_text, AES.block_size, style='pkcs7')
  return plain_text.decode(DEFAULT_ENCODING)