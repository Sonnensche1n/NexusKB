<style lang="less">
.kb-flow-node-prompt {
  width: 100%;
  height: 64px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background-color: var(--base-color);
  position: relative;
  .variable {
    position: absolute;
    left: 0;
    top: 0;
    z-index: 1;
    // display: none;
  }
  .editor {
    height: 100%;
    cursor: text;
    .w-e-modal {
      height: 260px;
      overflow: auto;
      .btn-close {
        z-index: 2;
      }
    }
    .w-e-text-container [data-slate-editor] p {
      margin: 4px 0;
    }
    .w-e-scroll {
      &::-webkit-scrollbar {
        display: none;
      }
    }
    .w-e-text-placeholder {
      top: 4px;
    }
  }
  .option {
    position: absolute;
    right: 4px;
    bottom: 0;
    .n-icon {
      cursor: pointer;
      &:hover {
        color: var(--primary-color);
      }
    }
  }
}
.kb-flow-node-prompt.dark {
  .editor {
    .w-e-modal {
      background-color: #303033;
      color: var(--text-color-base);
      border-color: var(--border-color);
    }
    .w-e-text-container {
      background-color: #303033;
      color: var(--text-color-base);
      blockquote {
        background-color: transparent;
        border-left-color: var(--success-color);
      }
      pre>code {
        background-color: #1A1A1A;
        text-shadow: none;
      }
    }
  }
}
</style>
<template>
  <div :class="`kb-flow-node-prompt ${themeType}`" @mousewheel.stop="">
    <!-- <prompt-variable class="variable" :id="`p-${attr.nodeId}-${attr.attrId}`" :attr="attr" @on-change="onPromptVaribleChange" /> -->
    <!-- <Toolbar class="toolbar" ref="toolbarRef" :editor="editorRef" :defaultConfig="toolbarConfig" :mode="mode" /> -->
    <Editor class="editor" v-model="valueHtml" :defaultConfig="editorConfig" :mode="mode" @onCreated="handleCreated" @onFocus="handleFocus" @customPaste="handlePaste" />
    <p class="option">
      <n-icon class="iconfont-kb icon-enlarge" @click="onEnlarge" />
    </p>
  </div>
</template>

<script>
import '@wangeditor/editor/dist/css/style.css'
import { defineComponent, ref, onBeforeUnmount, watch, shallowRef, onMounted, nextTick } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { localRead } from '@/libs/tools'
import EventBus from '@/libs/eventbus'
import PromptVariable from './PromptVariable.vue'
import { useNode } from '../../../mixin/node'
import { FOCUSED_ATTR_ID, FOCUSED_ATTR_VARIABLES } from './prompt.js'
import { Text } from 'slate'

export default defineComponent({
  components: {
    Editor, Toolbar, PromptVariable
  },
  props: {
    attr: Object
  },
  setup(props, context) {
    const message = useMessage()
    const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE)
    const onThemeTypeChange = (type) => {
      themeType.value = type
    }
    EventBus.on('on-theme-type-change', onThemeTypeChange)
    onBeforeUnmount(() => {
      EventBus.off('on-theme-type-change', onThemeTypeChange)
    })

    let { node } = useNode()
    const attr = props.attr
    const attrVal = attr['attrVal']
    let html = ''
    if (attrVal) {
      try {
        html = JSON.parse(attrVal)['html']
      } catch (e) {
      }
    }

    const toolbarRef = ref(null)
    const mode = ref('simple') // 'default' 或 'simple'

    // 编辑器实例，必须用 shallowRef
    const editorRef = shallowRef()
    // 内容 HTML
    const valueHtml = ref(html)

    /* 处理自定义元数据 getText 为空的问题 START */
    const nodeString = (node) => {
      if (node['type'] === 'variable') {
        return `{${node.value}}`
      }
	    if (Text.isText(node)) {
	      return node.text
	    } else {
	      return node.children.map(nodeString).join('')
	    }
	  }
    const getText = () => {
      const { children = [] } = editorRef.value
      let text = children.map(nodeString).join('\n')
      return text
    }
    /* 处理自定义元数据 getText 为空的问题 END */

    watch(valueHtml, (html) => {
      const editor = editorRef.value
      attr['attrVal'] = JSON.stringify({
        html,
        text: getText()
      })
    })

    const toolbarConfig = {
      insertKeys: {
        index: 0, // 插入的位置，基于当前的 toolbarKeys
        keys: ['variable']
      }
    }

    const editorConfig = {
      placeholder: '请输入内容...',
      hoverbarKeys: {
        'text': {
          // 如有 match 函数，则优先根据 match 判断，而忽略 element type
          match: (editor, n) => {
            if (!Text.isText(n)) return false
            let text = n['text']
            return text.endsWith('/')
            // let index = text.lastIndexOf('/')
            // if (index === -1) return false
            // let selection = {
            //   anchor: { path: [0, 0], offset: index + 1 }, // 结束位置
            //   focus: { path: [0, 0], offset: index } // 开始位置
            // }
            // editor.select(selection)
            // return true
          },
          menuKeys: ['variable'], // 定义你想要的 menu keys
        }
      }
    }

    // 组件销毁时，也及时销毁编辑器
    onBeforeUnmount(() => {
      const editor = editorRef.value
      if (editor == null) return
      editor.destroy()
    })
    onMounted(() => {
    })

    const handleCreated = (editor) => {
      editorRef.value = editor // 记录 editor 实例，重要！
    }

    const handleFocus = (editor) => {
      FOCUSED_ATTR_ID.value = `p-${attr.nodeId}-${attr.attrId}`
      FOCUSED_ATTR_VARIABLES.value = []
      let nodes = node._model.graph.getPredecessors(node).reverse() // 获取所有前序节点
      nodes.forEach(nd => {
        let ndData = nd.data
        FOCUSED_ATTR_VARIABLES.value.push({
          value: ndData.nodeId,
          label: ndData.nodeNm,
          children: (ndData.attrs || []).map(a => { // 需要过滤掉不同的数据类型，暂时不管
            return {
              nodeId: attr.nodeId,
              attrId: attr.attrId,
              value: `${ndData.nodeId}/${a.attrKey}`,
              label: a.attrLbl
            }
          })
        })
      })
    }

    const handlePaste = (editor, event) => {
      const html = event.clipboardData.getData('text/html') // 获取粘贴的 html
      const text = event.clipboardData.getData('text/plain') // 获取粘贴的纯文本
      // const rtf = event.clipboardData.getData('text/rtf') // 获取 rtf 数据（如从 word wsp 复制粘贴）
      editor.insertText(text)
      // 阻止默认的粘贴行为
      event.preventDefault()
      return false
    }

    // 获取内容
    const getContent = () => {
      const editor = editorRef.value
      if (editor == null) return ''
      return editor.getHtml()
    }

    const onPromptVaribleChange = ({ nodeId, attrId, label, value}) => {
      if (nodeId !== attr.nodeId || attrId !== attr.attrId) {
        return
      }
      const editor = editorRef.value
      editor.insertNode({
        type: 'variable',
        label,
        value,
        children: [{ text: '' }]
      })
      editor.restoreSelection()
      editor.deleteBackward()
      // editor.dangerouslyInsertHtml(`<b>{${value}}</b>`) // 用于自定义元素 getText能取到值
    }
    const onEnlarge = () => {
      context.emit('on-enlarge')
    }

    EventBus.on('on-prompt-variable-change', onPromptVaribleChange)
    onBeforeUnmount(() => {
      EventBus.off('on-prompt-variable-change', onPromptVaribleChange)
    })

    return {
      themeType, toolbarRef, editorRef, toolbarConfig, mode, valueHtml, editorConfig, handleCreated, handleFocus, handlePaste,
      getContent, onPromptVaribleChange, onEnlarge
    }
  }
})
</script>