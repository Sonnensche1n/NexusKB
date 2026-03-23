import Mock from 'mockjs'
const { Random } = Mock as any // 导出随机函数

const success = (data: any) => {
  return {
    code: 200,
    data,
    msg: '操作成功',
    success: true
  }
}

const successPage = (data: any) => {
  return {
    data,
    pageNum: 1,
    pageSize: 10,
    pages: 13,
    total: 130
  }
}

// 新增会话信息
const addChat = (req) => {
  return success(null)
}
// 修改会话信息
const editChat = (req) => {
  return success(null)
}
// 删除会话信息
const removeChat = (req) => {
  return success(null)
}

// 查询会话列表
const chatList = (req) => {
  return success([
    { chatId: Random.guid(), reposId: Random.guid(), chatTtl: Random.string(25) },
    { chatId: Random.guid(), reposId: Random.guid(), chatTtl: Random.string(25) }
  ])
}

// 查询会话列表
const messageList = (req) => {
  return success([
    { mesgId: Random.guid(), chatId: Random.guid(), mesgCntnt: Random.string(50), mesgTyp: 'text', crtRole: 'sys' },
    { mesgId: Random.guid(), chatId: Random.guid(), mesgCntnt: Random.string(50), mesgTyp: 'text', crtRole: 'sys'  }
  ])
}

export default {
  addChat, editChat, removeChat,
  chatList, messageList
}