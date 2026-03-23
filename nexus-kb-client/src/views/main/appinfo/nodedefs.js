export const allnodedefs = [
  {
    ndfId: 'start', ndfNm: '开始', ndfDesc: '', ndfCls: 'node', ndfIcon: '', width: 300,
    addInput: 'Y', addOutput: 'N', // 输入可以添加自定义属性，输出不能添加自定义属性
    incoming: '0', // 0或n个输入节点，初始化节点是使用
    outgoing: '1', // 1个输出节点
    attrs: [ // 这是固定的属性
      { attrId: 'start_question', ndfId: 'start', attrCls: 'ipt', attrKey: 'question', attrLbl: '用户问题', dataTyp: 'string', attrDesc: '', attrSrc: 'aut', notNull: 'Y', dftVal: '', compTyp: 'textarea' } // compTyp 前端组件: input,textarea,number,select,repostory知识库选择器,llm模型选择器,variable变量选择器,classify分类输入框 等等
    ]
  },
  {
    ndfId: 'end', ndfNm: '结束', ndfDesc: '', ndfCls: 'node', ndfIcon: '', width: 300,
    addInput: 'N', addOutput: 'Y', // 输入可以添加自定义属性，输出不能添加自定义属性
    incoming: '1',
    outgoing: '0',
    attrs: []
  },
  {
    ndfId: 'question_classify', ndfNm: '问题分类', ndfDesc: '', ndfCls: 'node', ndfIcon: '', width: 400,
    incoming: '1',
    outgoing: 'question_classify_classify', // question_classify_classify 的数量是多少则输出节点有多少
    attrs: [
      { attrId: 'question_classify_question', ndfId: 'question_classify', attrKey: 'question', attrLbl: '用户问题', attrCls: 'otr', attrSrc: 'var,ipt', attrVal: '', dataTyp: 'string', valSrc: 'var', builtIn: 'Y', compTyp: 'textarea' },
      { attrId: 'question_classify_backstory', ndfId: 'question_classify', attrKey: 'backstory', attrLbl: '分类背景', attrCls: 'otr', attrSrc: 'var,ipt', attrVal: '', dataTyp: 'string', valSrc: 'ipt', builtIn: 'Y', compTyp: 'textarea' },
      { attrId: 'question_classify_model', ndfId: 'question_classify', attrKey: 'model', attrLbl: 'AI模型', attrCls: 'otr', attrSrc: 'var,slt', attrVal: '', dataTyp: 'string', valSrc: 'slt', builtIn: 'Y', compTyp: 'llm' },
      { attrId: 'question_classify_classify', ndfId: 'question_classify', attrCls: 'otr', attrKey: 'classify', attrLbl: '分类', dataTyp: 'json', attrDesc: '', attrSrc: 'ipt', notNull: 'Y', dftVal: '', compTyp: 'classify' }
    ]
  },
  {
    ndfId: 'knowledge_base', ndfNm: '知识库检索', ndfDesc: '', ndfCls: 'node', ndfIcon: '',
    incoming: '1',
    outgoing: '1',
    attrs: [
      { attrId: 'knowledge_base_question', ndfId: 'knowledge_base', attrKey: 'question', attrLbl: '用户问题', attrCls: 'otr', attrSrc: 'var,ipt', attrVal: '', dataTyp: 'string', valSrc: 'var', builtIn: 'Y', compTyp: 'textarea' },
      { attrId: 'knowledge_base_repository', ndfId: 'knowledge_base', attrKey: 'repository', attrLbl: '选择知识库', attrCls: 'otr', attrSrc: 'var,slt', attrVal: '', dataTyp: 'json', valSrc: 'slt', builtIn: 'Y', compTyp: 'repository' },
      { attrId: 'knowledge_base_result', ndfId: 'knowledge_base', attrKey: 'result', attrLbl: '检索结果', attrCls: 'opt', attrSrc: 'aut', attrDesc: '结果样例展示', attrVal: '', dataTyp: 'json', valSrc: 'aut', builtIn: 'Y', compTyp: 'text' },
    ]
  },
  // { ndfId: 'condition_branch', ndfNm: '条件分支', ndfDesc: '', ndfCls: 'node', ndfIcon: '', attrs: [] },
  { 
    ndfId: 'llm', ndfNm: 'LLM对话', ndfDesc: '', ndfCls: 'node', ndfIcon: '', width: 400,
    incoming: '1',
    outgoing: '1',
    attrs: [
      // 还有动态的输入，与输出参数，在提示词中可以引用输入参数
      { attrId: 'llm_model', ndfId: 'llm', attrCls: 'otr', attrKey: 'model', attrLbl: 'AI模型', dataTyp: 'string', attrDesc: '', attrSrc: 'slt,var', notNull: 'Y', dftVal: '', builtIn: 'Y', compTyp: 'llm' },
      { attrId: 'llm_prompt', ndfId: 'llm', attrCls: 'otr', attrKey: 'prompt', attrLbl: '提示词', dataTyp: 'string', attrDesc: '', attrSrc: 'ipt,var', notNull: 'N', dftVal: '', builtIn: 'Y', compTyp: 'textarea' },
      { attrId: 'llm_result', ndfId: 'llm', attrCls: 'opt', attrKey: 'result', attrLbl: 'LLM生成内容', dataTyp: 'string', attrDesc: '', attrSrc: 'aut', notNull: 'Y', dftVal: '', builtIn: 'Y', compTyp: 'textarea' }
    ]
  }
]