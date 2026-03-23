import { v4 as uuidv4 } from 'uuid'
/**
 * 生成随机字符串
 * @param {Boolean} randomFlag 是否任意长度
 * @param {Number} min 任意长度最小位[固定位数]
 * @param {Number} max 任意长度最大位
 */
export const random = (randomFlag:boolean, min:number, max:number) => {
  let str = ''
  let range = min
  // let arr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
  let arr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
  // 随机产生
  if (randomFlag) {
    range = Math.round(Math.random() * (max - min)) + min
  }
  for (let i = 0; i < range; i++) {
    str += arr[Math.round(Math.random() * (arr.length - 1))]
  }
  return str
}
/**
 * 获取指定大小范围的整数
 * @param {*} minNum
 * @param {*} maxNum
 */
export const randomNum = function (minNum:number, maxNum:number) {
  let num = 0
  switch (arguments.length) {
    case 1:
      num = parseInt((Math.random() * minNum + 1).toString(), 10)
      break
    case 2:
      num = parseInt((Math.random() * (maxNum - minNum + 1) + minNum).toString(), 10)
      break
  }
  return num
}
/**
 * 某字符串是否为空或长度为0或由空白符构成
 * @param {*} str
 */
export const isBlank = (str:string) => {
  return (str + '').replace(/(^\s*)|(\s*$)/g, '') === ''
}
/**
 * 判断某字符串是否为空，为空的标准是 null或undefined或length==0
 * @param {*} str
 */
export const isEmpty = (str:string) => {
  let v1 = str === undefined || str === null
  if (v1) return true
  return isBlank(str)
}

/**
 * 深拷贝对象
 * @param {*} object
 */
export const deepCopy = (object:any) => {
  let result = Array.isArray(object) ? [] as any[] : {} as any
  for (let key in object) {
    if (object.hasOwnProperty(key)) {
      if (typeof object[key] === 'object' && object[key] !== null) {
        result[key] = deepCopy(object[key]) // 递归复制
      } else {
        result[key] = object[key]
      }
    }
  }
  return result
}

/**
 * 数组按属性排序
 * array.sort(compare('key'))
 * type: -1 倒序， 1 正序
 */
export const compare = (property:any, type:number) => {
  if (type === undefined) type = 1
  return (a:any, b:any) => {
    let value1 = a[property]
    if (value1 === null || value1 === undefined) value1 = ''
    let value2 = b[property]
    if (value2 === null || value2 === undefined) value2 = ''
    let v1 = Number(value1)
    let v2 = Number(value2)
    if (isNaN(v1)) v1 = value1.charCodeAt()
    if (isNaN(v2)) v2 = value2.charCodeAt()
    if (type > 0) return v1 - v2
    else return v2 - v1
  }
}

/**
 * 将 source 的属性拷贝到 target 中
 * @param {*} target
 * @param {*} source
 * @param {*} converter 有时候 value 可能需要转换一下值
 */
export const copyProp = (target:any, source:any, converter:Function) => {
  if (!target || !source) return
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      let value = source[key]
      if (converter) value = converter(key, value)
      target[key] = value
    }
  }
}
/**
 * 将 source 的属性拷贝到 target 中
 * 只拷贝 target 中存在的属性
 * @param {*} target
 * @param {*} source
 * @param {*} converter 有时候 value 可能需要转换一下值
 */
export const copySelfProp = (target:any, source:any, converter:Function) => {
  if (!target || !source) return
  for (const key in target) {
    if (target.hasOwnProperty(key)) {
      let value = source[key]
      if (converter) value = converter(key, value)
      target[key] = value
    }
  }
}
/**
 * 是否数组
 * @param value
 * @returns 
 */
export const isNumber = (value:any) => {
  return !isNaN(value)
}
/**
 * 是否包含中文
 * @param value
 * @returns 
 */
export const isContainChinese = (value:string) => {
  return /[\u4E00-\u9FA5]/g.test(value)
}
/**
 * 首字母转小写
 * @param value
 * @returns 
 */
export const lowerCaseFirst = (value:string) => {
  return value.charAt(0).toLowerCase() + value.slice(1)
}
/**
 * 首字母转大写
 * @param value
 * @returns 
 */
export const upperCaseFirst = (value:string) => {
  return value.charAt(0).toUpperCase() + value.slice(1)
}
/**
 * 获取文件内容
 * @param name
 * @returns
 */
export const loadFile = (name:string) => {
  // name为文件所在位置
  let xhr = new XMLHttpRequest()
  const okStatus = document.location.protocol === 'file:' ? 0 : 200
  xhr.open('GET', name, false)
  xhr.overrideMimeType('text/html;charset=utf-8') // 默认为utf-8
  xhr.send(null)
  return xhr.status === okStatus ? xhr.responseText : null
}

/**
 * 存储数据到 localStorage
 * @param key
 * @param value
 */
export const localSave = (key:string, value:any) => {
  if (typeof value === 'object') {
    localStorage.setItem(key, JSON.stringify(value))
  } else {
    localStorage.setItem(key, value)
  }
}

/**
 * 从 localStorage 获取数据
 * @param {*} key
 */
export const localRead = (key:string) => {
  let value = localStorage.getItem(key) as (string | null)
  if (value === null) {
    return null
  }
  if (isEmpty(value)) {
    return null
  }
  try {
    return JSON.parse(value)
  } catch (error) {
    return value
  }
}
/**
 * 从 localStorage 删除数据
 * @param key
 */
export const localRemove = (key:string) => {
  localStorage.removeItem(key)
}

export const RGBA_COLOR_REGEX = /^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*[\d\.]+\s*)?\)$/
export const HEX_COLOR_REGEX = /^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$/
/**
 * 是否16进制颜色
 * @param color
 * @returns 
 */
export const isHexColor = (color:string) => {
  return HEX_COLOR_REGEX.test(color);
}

/**
 * 是否rgba颜色
 * @param color
 * @returns
 */
export const isRgbaColor = (color:string) => {
  return RGBA_COLOR_REGEX.test(color);
}

export const rgbaToHex = (rgba: string): string => {
  // 移除可能存在的前缀 'rgba(' 和后缀 ')'
  const rgbaTrimmed = rgba.replace(/rgba?[\s+]?\(/i, '').replace(/\)[\s+]?/i, '')
  // 将rgbaTrimmed拆分为数组，包含红、绿、蓝和alpha值
  const values = rgbaTrimmed.split(/[\s,]+/)
  const r = parseInt(values[0], 10)
  const g = parseInt(values[1], 10)
  const b = parseInt(values[2], 10)
  const a = parseFloat(values[3])
  // 将RGB值转换为十六进制形式
  const toHex = (value: number) => {
      let hex = Math.round(value).toString(16)
      return hex.length === 1 ? '0' + hex : hex
  };
  const hexColor = `#${toHex(r)}${toHex(g)}${toHex(b)}`
  // 如果需要，也可以返回包含alpha的HEX颜色，例如 #AARRGGBB
  // const alphaHex = Math.round(a * 255).toString(16);
  // return `#${alphaHex}${hexColor.slice(1)}`;
  return hexColor
}

export const hexToRgba = (color:string, alpha:number = 1) => {
  // 去掉可能存在的'#'字符
  color = color.replace('#', '')
  // 确保hex颜色是6位的，如果不是则复制每一对数字以填充6位
  if (color.length === 3) {
    color = color.split('').map(c => c + c).join('')
  }
  // 将16进制颜色转换为RGB数组
  const rgb = [
    parseInt(color.substring(0, 2), 16),
    parseInt(color.substring(2, 4), 16),
    parseInt(color.substring(4, 6), 16)
  ]
  // 构建并返回RGBA颜色字符串
  return `rgba(${rgb.join()}, ${alpha})`
}

/**
 * 修改rgba的透明度
 * @param color
 * @param alpha
 * @returns
 */
export const modifyColorAlpha = (color:string, alpha:number) => {
  // 匹配输入的RGBA颜色字符串
  if (isRgbaColor(color)) {
    const match = color.match(RGBA_COLOR_REGEX);
    // 如果匹配成功
    if (match) {
      // 解析出RGBA的各部分
      const r = parseInt(match[1], 10);
      const g = parseInt(match[2], 10);
      const b = parseInt(match[3], 10);
      const a = match[4] ? parseFloat(match[4]) : 1; // 如果没有指定Alpha，默认为1
      // 使用新的Alpha值构建新的RGBA字符串
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
  } else if (isHexColor(color)) {
    return hexToRgba(color, alpha)
  } else {
    return color
  }
}

/**
 * 生成相近的颜色
 * @param color
 * @param count
 * @returns
 */
export const similarColors = (color:string, count:number, adjustment:number = 10) => {
  let isHex = isHexColor(color)
  let baseColor = isHex ? hexToRgba(color) : color
  const match = baseColor.match(RGBA_COLOR_REGEX)
  let colors:string[] = []
    // 如果匹配成功
  if (!match) {
    for (let i = 0; i < count; i++) {
      colors.push(color)
    }
    return colors
  }
  // 解析出RGBA的各部分
  const r = parseInt(match[1], 10)
  const g = parseInt(match[2], 10)
  const b = parseInt(match[3], 10)
  
  for (let i = 0; i < count; i++) {
    let rgb = {
      r: Math.min(255, Math.max(0, r + Math.floor(Math.random() * adjustment * 2) - adjustment)),
      g: Math.min(255, Math.max(0, g + Math.floor(Math.random() * adjustment * 2) - adjustment)),
      b: Math.min(255, Math.max(0, b + Math.floor(Math.random() * adjustment * 2) - adjustment))
    }
    let newColor = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 1)`
    if (isHex) {
      colors.push(rgbaToHex(newColor))
    } else {
      colors.push(newColor)
    }
  }
  return colors
}

/**
 * 获取uuid
 * @returns uuid
 */
export const uuid = () => {
  return uuidv4().replaceAll('-', '')
}

export const bytesToSize = (bytes:number, separator:string = '') => {
  const sizes = ['B', 'K', 'M', 'G', 'T'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)}${separator}${sizes[i]}`;
}

export const copyToClipboard = (text:string) => {
  // navigator clipboard 需要https等安全上下文
  if (navigator.clipboard && window.isSecureContext) {
    // navigator clipboard 向剪贴板写文本
    return navigator.clipboard.writeText(text)
  } else {
    // 创建text area
    let textArea = document.createElement('textarea')
    textArea.value = text
    // 使text area不在viewport，同时设置不可见
    textArea.style.position = 'absolute'
    textArea.style.opacity = '0'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    return new Promise<void>((res, rej) => {
      // 执行复制命令并移除文本框
      document.execCommand('copy') ? res() : rej()
      textArea.remove()
    })
  }
}