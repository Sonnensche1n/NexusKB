import axios from 'axios'
import useUserStore from '@/store/user'
import { baseURL } from '@/config'

// 设置baseUrl
axios.defaults.baseURL = baseURL
// 设置请求头
axios.defaults.headers['Content-Type'] = 'application/json;charset=UTF-8'
// 设置超时
axios.defaults.timeout = 30000
// 请求拦截器
axios.interceptors.request.use(
  config => {
    const token = useUserStore().getToken
    token && (config.headers['token'] = token)
    return config
  },
  error => {
    return Promise.reject(error)
  }
);

// 响应拦截器
axios.interceptors.response.use(
  response => {
    if (response.status == 200) {
      return Promise.resolve(response)
    } else {
      return Promise.reject(response)
    }
  },
  error => {
    if (!('response' in error)) {
      return Promise.reject(error)
    }
    let data = error.response.data
    if (typeof data === 'string') {
      data = {
        'code': '9999',
        'success': false,
        'data': null,
        'msg': data
      }
    }
    setTimeout(() => {
      if (data.msg) { // 在 catch 中将消息设置为空则不会弹出消息框了
        if (window.$message) {
          window.$message.destroyAll()
          window.$message.error(data.msg, {
            closable: true, duration: 10000, keepAliveOnHover: false
          })
        }
      }
    }, 200)
    return Promise.reject(data)
  }
)

// 封装post/get请求
export default {
  post(url:string, data:any, options:any = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'post',
        url,
        data,
        //data: qs.stringify(data), //参数序列化
        ...options
      })
      .then(res => {
        resolve(res.data)
      })
      .catch(err => {
        reject(err)
      })
    })
  },
  get(url:string, data:any, options:any = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'get',
        url,
        params: data,
        ...options
      })
      .then(res => {
        resolve(res.data)
      })
      .catch(err => {
        reject(err)
      })
    })
  },
  put(url:string, data:any, options:any = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'put',
        url,
        data,
        ...options
      })
      .then(res => {
        resolve(res.data)
      })
      .catch(err => {
        reject(err)
      })
    })
  },
  delete(url:string, data:any, options:any = {}) {
    return new Promise((resolve, reject) => {
      axios({
        method: 'delete',
        url,
        data,
        ...options
      })
      .then(res => {
        resolve(res.data)
      })
      .catch(err => {
        reject(err)
      })
    })
  },
  async fetch(url:string, data:any, callback:Function, options:any = {}) {
    const response = await fetch(axios.defaults.baseURL + url,
      {
        method: 'post',
        responseType: 'stream',
        headers: {
          token: useUserStore().getToken,
          'Content-Type': axios.defaults.headers['Content-Type'],
        },
        body: JSON.stringify(data),
        ...options
      }
    )
    // ok字段判断是否成功获取到数据流
    if (!response.ok) {
      if (callback) callback()
      // throw new Error('Network response was not ok')
      return
    }
    // 用来获取一个可读的流的读取器（Reader）以流的方式处理响应体数据
    const reader = response.body?.getReader()
    if (reader === undefined) {
      if (callback) callback()
      return
    }
    // 将流中的字节数据解码为文本字符串
    const textDecoder = new TextDecoder()
    let result = true
    while (result) {
      // done表示流是否已经完成读取  value包含读取到的数据块
      const { done, value } = await reader.read()
      if (done) {
        result = false
        break
      }
      // 拿到的value就是后端分段返回的数据，大多是以data:开头的字符串
      // 需要通过decode方法处理数据块，例如转换为文本或进行其他操作
      textDecoder.decode(value).split('\n').forEach(val => {
        if (!val) return
        try {
          // 后端返回的流式数据一般都是以data:开头的字符，排除掉data:后就是需要的数据
          // 具体返回结构可以跟后端约定
          if (val.startsWith(': ping')) {
            return
          }
          if (callback) {
            let message = val?.replace('data:', '') || ''
            callback(message)
          }
        } catch (err) {
          console.error(err)
        }
      })
    }
  }
}
