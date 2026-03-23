import CryptoJS from 'crypto-js'
const key = CryptoJS.enc.Utf8.parse('X74%B>P2A|$w"!vC&P)xbk1"K&&03Lyt') // 密钥 后端提供，暂时这样
const iv = CryptoJS.enc.Utf8.parse('VvIuBncwj8g37s69') // 偏移量
/**
 * AES加密 ：字符串 key iv  返回base64
 */
export function aes_encrypt(text:string) {
  const srcs = CryptoJS.enc.Utf8.parse(text)
  const encrypted = CryptoJS.AES.encrypt(srcs, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })
  return CryptoJS.enc.Base64.stringify(encrypted.ciphertext)
}

/**
 * AES 解密 ：字符串 key iv  返回base64
 *  */
export function aes_decrypt(text:string) {
  const base64 = CryptoJS.enc.Base64.parse(text)
  const src = CryptoJS.enc.Base64.stringify(base64)
  const decrypt = CryptoJS.AES.decrypt(src, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })
  return CryptoJS.enc.Utf8.stringify(decrypt)
}

