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

// 新增知识库信息
const addRepository = (req) => {
  return success(null)
}
// 修改知识库信息
const editRepository = (req) => {
  return success(null)
}
// 删除知识库信息
const removeRepository = (req) => {
  return success(null)
}

// 查询知识库列表
const repositoryList = (req) => {
  return success([
    { reposId: Random.guid(), reposNm: Random.string(10), reposDesc: Random.string(100) },
    { reposId: Random.guid(), reposNm: Random.string(10), reposDesc: Random.string(100) }
  ])
}

export default {
  addRepository, editRepository, removeRepository,
  repositoryList
}