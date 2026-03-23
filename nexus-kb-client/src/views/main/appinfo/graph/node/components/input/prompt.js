
import { h } from 'snabbdom'
import { Boot, DomEditor } from '@wangeditor/editor'
import { ref } from 'vue'
import EventBus from '@/libs/eventbus'

export const FOCUSED_ATTR_ID = ref('')
export const FOCUSED_ATTR_VARIABLES = ref([])
class VariableMenu {
    constructor() {
      this.title = '变量引用'
      // this.iconSvg = '<svg >...</svg>'
      this.tag = 'button'
      this.showModal = true
      this.modalWidth = 300
    }
    // 菜单是否需要激活（如选中加粗文本，“加粗”菜单会激活），用不到则返回 false
    isActive(editor) {
      return false
    }
    // 获取菜单执行时的 value ，用不到则返回空 字符串或 false
    getValue(editor) {
      return ''
    }
    // 菜单是否需要禁用（如选中 H1 ，“引用”菜单被禁用），用不到则返回 false
    isDisabled(editor) {
      return false
    }
    // 点击菜单时触发的函数
    exec(editor, value) {
      // Modal menu ，这个函数不用写，空着即可
    }
    // 弹出框 modal 的定位：1. 返回某一个 SlateNode； 2. 返回 null （根据当前选区自动定位）
    getModalPositionNode(editor) {
      return null // modal 依据选区定位
    }
    // 定义 modal 内部的 DOM Element
    getModalContentElem(editor) {
      // let el = document.getElementById(FOCUSED_ATTR_ID.value)
      // console.log(el)
      // // el = el.cloneNode(true) // true 表示深复制，包括所有后代节点
      // el.style['display'] = 'block'
      let el = document.createElement('div')
      let items = []
      FOCUSED_ATTR_VARIABLES.value.forEach(variable => {
        let childs = []
        variable.children.forEach(child => {
          childs.push(`<div class="n-thing">
            <div class="n-thing-main">
              <div class="n-thing-main__content" nodeid="${child.nodeId}" attrid="${child.attrId}" value="${child.value}" label="${variable.label}/${child.label}">${child.label}</div>
            </div>
          </div>`)
        })
        items.push(`
        <div class="n-collapse-item n-collapse-item--left-arrow-placement n-collapse-item--active n-collapse-item--trigger-area-main n-collapse-item--trigger-area-extra n-collapse-item--trigger-area-arrow">
          <div class="n-collapse-item__header n-collapse-item__header--active">
            <div class="n-collapse-item__header-main">
              <div class="n-collapse-item-arrow" data-arrow="true"><i class="n-base-icon"></i></div>${variable.label}
            </div>
            <div class="n-collapse-item__header-extra" data-extra="true"></div>
          </div>
          <div class="n-collapse-item__content-wrapper">
            <div class="n-collapse-item__content-inner">
              ${childs.join('')}
            </div>
          </div>
        </div>
        `)
      })
      el.innerHTML = `
      <div class="n-collapse kb-flow-node-prompt-variable variable">
        ${items.join('')}
      </div>
      `
      el.onclick = function(e) {
        if (e.target.className.indexOf('n-thing-main__content') === -1) {
          return
        }
        const { nodeid, attrid, value, label } = e.target.attributes
        if (!value) {
          return
        }
        EventBus.emit('on-prompt-variable-change', {
          nodeId: nodeid.value, attrId: attrid.value, value: value.value, label: label.value
        })
      }
      return el
    }
  }
  
  const variableMenu = {
    key: 'variable', // 定义 menu key ：要保证唯一、不重复（重要）
    factory () {
      return new VariableMenu() // 把 `YourMenuClass` 替换为你菜单的 class
    }
  }
  
  function variableToHtml(elem, childrenHtml) {
    // 获取附件元素的数据
    const { value = '', label = '' } = elem
    // 生成 HTML 代码
    const html = `<span
      data-w-e-type="variable"
      data-w-e-is-void
      data-w-e-is-inline
      data-value="${value}"
      data-label="${label}"
    >${label}</span>`
    return html
  }
  
  const elemToHtmlConf = {
    type: 'variable', // 新元素的 type ，重要！！！
    elemToHtml: variableToHtml,
  }
  
  Boot.registerElemToHtml(elemToHtmlConf)
  
  function parseVariableHtml(domElem, children, editor) {                                                     // JS 语法
    // 从 DOM element 中获取“附件”的信息
    const value = domElem.getAttribute('data-value') || ''
    const label = domElem.getAttribute('data-label') || ''
    // 生成“附件”元素（按照此前约定的数据结构）
    return {
      type: 'variable',
      value,
      label,
      children: [{ text: '' }], // void node 必须有 children ，其中有一个空字符串，重要！！！
    }
  }
  
  const parseHtmlConf = {
    selector: 'span[data-w-e-type="variable"]', // CSS 选择器，匹配特定的 HTML 标签
    parseElemHtml: parseVariableHtml,
  }
  
  Boot.registerParseElemHtml(parseHtmlConf)
  
  function renderVariable(elem, children, editor) {
    // 获取“附件”的数据，参考上文 myResume 数据结构
    const { label } = elem
    const vnode = h(
      'span',
      {
        style: { display: 'inline-block', marginLeft: '4px', marginRight: '4px' }
      },
      [ `{${label}}` ]
    )
    return vnode
  }
  
  const renderElemConf = {
    type: 'variable', // 新元素 type ，重要！！！
    renderElem: renderVariable,
  }
  
  Boot.registerRenderElem(renderElemConf)
  
  function withVariable(editor) {
    const { insertText, isInline, isVoid } = editor // 获取当前 editor API
    const newEditor = editor
    // 重写 insertText
    newEditor.insertText = (t) => {
      if (t === '/') {
      }
      insertText(t)
    }
    newEditor.isInline = elem => {
      const type = DomEditor.getNodeType(elem)
      if (type === 'variable') return true // 针对 type: variable ，设置为 inline
      return isInline(elem)
    }
  
    newEditor.isVoid = elem => {
      const type = DomEditor.getNodeType(elem)
      if (type === 'variable') return true // 针对 type: variable ，设置为 void
      return isVoid(elem)
    }
    return newEditor
  }
  Boot.registerMenu(variableMenu)
  Boot.registerPlugin(withVariable)