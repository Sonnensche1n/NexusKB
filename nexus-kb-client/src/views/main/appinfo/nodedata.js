export const nodedatas = [
  {
    nodeId: 'node1', ndfId: 'start', nodeNm: '流程开始', nodeDesc: '流程开始', width: 260, posX: 100, posY: 160,
    nodeDef: {
      addInput: 'Y', addOutput: 'N'
    },
    ports: [
      { portId: 'port1-1', portTyp: 'outgoing', nodeId: 'node1' }
    ],
    attrs: [
      { nodeId: 'node1', attrId: 'start_question', attrKey: 'question', attrLbl: '用户问题', attrCls: 'ipt', attrVal: '明天天气怎么样？', dataTyp: 'string', valSrc: 'aut', builtIn: 'Y', compTyp: 'textarea' } // var 变量引用、ipt 手动输入、slt 手动选择、aut 自动设置
    ] // 节点变量
  },
  {
    nodeId: 'node2', ndfId: 'question_classify', nodeNm: '问题分类', nodeDesc: '问题分类', width: 400, posX: 600, posY: 160,
    ports: [
      { portId: 'port2-1', portTyp: 'incoming', nodeId: 'node2' },
      { portId: 'port2-2', portTyp: 'outgoing', nodeId: 'node2', attrId: 'question_classify_classify', valKey: 'classid1', posY: 0 },
      { portId: 'port2-3', portTyp: 'outgoing', nodeId: 'node2', attrId: 'question_classify_classify', valKey: 'classid2', posY: 0 },
      { portId: 'port2-4', portTyp: 'outgoing', nodeId: 'node2', attrId: 'question_classify_classify', valKey: 'classid3', posY: 0 }
    ],
    attrs: [
      { nodeId: 'node2', attrId: 'question_classify_question', attrKey: 'question', attrLbl: '用户问题', attrCls: 'otr', attrSrc: 'var,ipt', attrVal: 'node1/start_question', dataTyp: 'string', valSrc: 'var', builtIn: 'Y', compTyp: 'textarea' },
      { nodeId: 'node2', attrId: 'question_classify_backstory', attrKey: 'backstory', attrLbl: '背景知识', attrCls: 'otr', attrSrc: 'var,ipt', attrVal: '--', dataTyp: 'string', valSrc: 'ipt', builtIn: 'Y', compTyp: 'textarea' },
      { nodeId: 'node2', attrId: 'question_classify_llm', attrKey: 'llm', attrLbl: 'AI模型', attrCls: 'otr', attrSrc: 'var,slt', attrVal: 'ollama/qwen2', dataTyp: 'string', valSrc: 'slt', builtIn: 'Y', compTyp: 'llm' },
      { nodeId: 'node2', attrId: 'question_classify_classify', attrKey: 'classify', attrLbl: '分类', attrCls: 'otr', attrSrc: 'ipt', attrVal: '[{"key": "classid1", "value": "分类1"},{"key": "classid2", "value": "分类2"},{"key": "classid3", "value": "分类3"}]', dataTyp: 'string', valSrc: 'ipt', builtIn: 'Y', compTyp: 'classify' },
    ]
  }
]

export const edgedatas = [
  {
    edgeId: 'edge1',
    srcId: 'node1',
    tgtId: 'node2',
    srcPortId: 'port1-1',
    tgtPortId: 'port2-1'
  }
]