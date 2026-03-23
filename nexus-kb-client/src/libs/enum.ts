export const THEME_TYPE_KEY = 'theme'
export const THEME_COLOR_KEY = 'color'
export const TEME_NAVIGATION_KEY = 'navigation'
export const DEFAULT_THEME_TYPE = 'light'
export const DEFAULT_THEME_COLOR = '#0D9488'
export const DEFAULT_THEME_NAVIGATION = 'default'
export const CURRENT_REPOS_ID_KEY = 'current_repos_id'

// 模型首选项参数代码
export const SYSTEM_MODEL_PREFERENCE_PARAM_CODE = 'model_preference'

// 文件图标
export const FILE_TYPE_ICON_MAP = {
  pdf: 'iconfont-kb icon-pdf1',
  txt: 'iconfont-kb icon-txt1',
  docx: 'iconfont-kb icon-word1',
  md: 'iconfont-kb icon-markdown',
  html: 'iconfont-kb icon-html5',
  dcmt: 'iconfont-kb icon-document',
  pptx: 'iconfont-kb icon-ppt1',
  mp4: 'iconfont-kb icon-video',
  avi: 'iconfont-kb icon-video',
  mkv: 'iconfont-kb icon-video',
  mov: 'iconfont-kb icon-video',
  wmv: 'iconfont-kb icon-video',
  flv: 'iconfont-kb icon-video',
  webm: 'iconfont-kb icon-video',
  mp3: 'iconfont-kb icon-audio',
  wav: 'iconfont-kb icon-audio',
  ogg: 'iconfont-kb icon-audio',
  flac: 'iconfont-kb icon-audio',
  link: 'iconfont-kb icon-link1',
  csv: 'iconfont-kb icon-csv',
  xlsx: 'iconfont-kb icon-excel',
  xls: 'iconfont-kb icon-excel'
}

// 团队人员角色
export const AUTH_TEAM_ROLE_TYPE = {
  creator: '创建者',
  manager: '管理员',
  member: '成员'
}
// 权限类型
export const COMMON_AUTH_RANGE_TYPE = {
  prvt: '仅自己可见', // 私有
  team: '仅团队可见', // 团队
  pblc: '所有人可见' // 公开
}
// 操作权限类型
export const COMMON_AUTH_OPTION_TYPE = {
  visit: '访问',
  alter: '修改'
}
// 数据集索引状态
export const DATASET_INDEX_STATUS_TYPE = {
  nobd: '不构建',
  new: '新建',
  order: '排队中',
  index: '索引中',
  ready: '已就绪',
  error: '索引失败'
}

// 数据集索引类型
export const DATASET_INDEX_TYPE = {
  index: { label: '索引', value: 'index', icon: 'iconfont-kb icon-dataset1' },
  precis: { label: '摘要', value: 'precis', icon: 'iconfont-kb icon-document' },
  qanswer: { label: 'Q&A', value: 'qanswer', icon: 'iconfont-kb icon-qa' },
  triplet: { label: '图谱', value: 'triplet', icon: 'iconfont-kb icon-triplet1' }
}

// 数据集启用状态
export const DATASET_ENABLE_STATUS_TYPE = {
  enb: '已启用',
  une: '未启用'
}

// 文档类型
export const DOCUMENT_TYPE = {
  md: 'Markdown',
  rt: '富文本'
}

// 流程节点属性值来源 var 变量引用、ipt 手动输入、slt 手动选择、aut 自动设置
export const NODE_ATTR_VALUE_SOURCE_TYPE = {
  var: { label: '变量引用', value: 'var', icon: 'iconfont-kb icon-variable' },
  ipt: { label: '手动输入', value: 'ipt', icon: 'iconfont-kb icon-input' },
  slt: { label: '手动选择', value: 'slt', icon: 'iconfont-kb icon-select' },
  aut: { label: '自动设置', value: 'aut', icon: 'iconfont-kb icon-autoset' }
}

// 流程节点属性值数据类型
export const NODE_ATTR_VALUE_DATA_TYPE = {
  string: { label: '文本', value: 'string', icon: 'iconfont-kb icon-text' },
  text: { label: '段落', value: 'text', icon: 'iconfont-kb icon-document' },
  number: { label: '数字', value: 'number', icon: 'iconfont-kb icon-number' },
  selection: { label: '下拉选项', value: 'selection', icon: 'iconfont-kb icon-select' },
  // custom: { label: '自定义变量', value: 'custom', icon: 'iconfont-kb icon-variable1' },
  // json: { label: 'json字符串', value: 'json', icon: 'iconfont-kb icon-codenotequalvariant' }
}

// 应用发布状态
export const APPINFO_RELEASE_STATUS = {
  rlsed: {
    label: '已发布', value: 'rlsed'
  },
  unrlse: {
    label: '未发布', value: 'unrlse'
  }
}

// 条件分支类型
// 为空，不为空，等于，不等于，包含，不包含，开始为，结束为，大于，大于等于，小于，小于等于，长度等于，长度不等于，长度大于，长度大于等于，长度小于，长度小于等于
export const NODE_ATTR_CONDITION_TYPE = {
  null: { label: '为空', value: 'null' },
  nnull: { label: '不为空', value: 'nnull' },
  eq: { label: '等于', value: 'eq' },
  neq: { label: '不等于', value: 'neq' },
  in: { label: '包含', value: 'in' },
  nin: { label: '不包含', value: 'nin' },
  stw: { label: '开始为', value: 'stw' },
  edw: { label: '结束为', value: 'edw' },
  gt: { label: '大于', value: 'gt' },
  gte: { label: '大于等于', value: 'gte' },
  lt: { label: '小于', value: 'lt' },
  lte: { label: '小于等于', value: 'lte' },
  leneq: { label: '长度等于', value: 'leneq' },
  lenneq: { label: '长度不等于', value: 'lenneq' },
  lengt: { label: '长度大于', value: 'lengt' },
  lengte: { label: '长度大于等于', value: 'lengte' },
  lenlt: { label: '长度小于', value: 'lenlt' },
  lenlte:{ label: '长度小于等于', value: 'lenlte' }
}

// 模型类型
export const LLM_MODEL_TYPE = {
  llm: { label: 'LLM', value: 'llm' },
  'text-embedding': { label: 'TEXT-EMBEDDING', value: 'text-embedding' },
  tts: { label: 'TTS', value: 'tts' },
  rerank: { label: 'RERANK', value: 'rerank' },
  speech2text: { label: 'SPEECH2TEXT', value: 'speech2text' }
}