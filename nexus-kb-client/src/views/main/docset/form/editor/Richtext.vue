<style lang="less">
.kb-richtext-edit {
  height: 100%;
  z-index: 2024;
  border: 1px solid var(--border-color);
  background-color: var(--base-color);
  .toolbar {
    border-bottom: 1px solid var(--border-color);
  }
}
.kb-richtext-edit.dark {
  .toolbar {
    border-bottom: 1px solid var(--border-color);
    .w-e-bar {
      background-color: var(--base-color);
      color: var(--text-color-3);
      svg {
        fill: var(--text-color-3);
      }
      .w-e-bar-divider {
        background-color: var(--border-color);
      }
      .w-e-bar-item {
        button:hover {
          background-color: var(--primary-color-hover);
          color: var(--text-color-3);
        }
        .w-e-select-list {
          background-color: var(--base-color);
          border-color: var(--border-color);
        }
        .w-e-select-list ul li:hover {
          background-color: var(--primary-color-hover);
        }
        .w-e-select-list ul .selected {
          background-color: var(--primary-color);
        }
        .active {
          background-color: var(--primary-color-pressed);
          color: var(--text-color-3);
        }
        .w-e-drop-panel {
          background-color: var(--base-color);
          border-color: var(--border-color);
          .w-e-panel-content-color {
            li {
              border-color: var(--border-color);
            }
          }
        }
        .w-e-panel-content-table {
          background-color: var(--base-color);
          td {
            border-color: var(--border-color);
          }
        }
      }
      .w-e-bar-item-group {
        .w-e-bar-item-menus-container {
          background-color: var(--base-color);
          border-color: var(--border-color);
          .w-e-bar-item button {
            color: var(--text-color-3);
          }
        }
      }
    }
  }
  .editor {
    .w-e-text-container {
      .w-e-scroll {
        &::-webkit-scrollbar {
          background-color: var(--base-color);
          width: 6px;
        }
        &::-webkit-scrollbar-thumb {
          background-color: var(--border-color);
          border-radius: 5px;
        }
      }
      background-color: var(--base-color);
      color: var(--text-color-base);
      blockquote {
        background-color: var(--divider-color);
        border-left-color: var(--primary-color);
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
  <div :class="`kb-richtext-edit ${themeType}`">
    <Toolbar class="toolbar" ref="toolbarRef" :editor="editorRef" :defaultConfig="toolbarConfig" :mode="mode" />
    <Editor class="editor" v-model="valueHtml" :style="{height: `calc(100% - ${toolbarRefHeight}px)`}" :defaultConfig="editorConfig" :mode="mode" @onCreated="handleCreated" />
  </div>
</template>

<script>
import '@wangeditor/editor/dist/css/style.css'
import { defineComponent, ref, onBeforeUnmount, computed, shallowRef, onMounted, nextTick } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { localRead } from '@/libs/tools'
import EventBus from '@/libs/eventbus'
export default defineComponent({
  components: {
    Editor, Toolbar
  },
  props: {
    content: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const message = useMessage()
    const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE)
    const onThemeTypeChange = (type) => {
      themeType.value = type
    }
    EventBus.on('on-theme-type-change', onThemeTypeChange)
    onBeforeUnmount(() => {
      EventBus.off('on-theme-type-change', onThemeTypeChange)
    })

    const toolbarRef = ref(null)
    const mode = ref('default') // 'default' 或 'simple'

    // 编辑器实例，必须用 shallowRef
    const editorRef = shallowRef()
    // 内容 HTML
    const valueHtml = ref(props.content)

    const toolbarConfig = {
      excludeKeys: [ 'group-video', 'insertLink', 'insertImage' ]
    }
    const editorConfig = {
      placeholder: '请输入内容...',
      MENU_CONF: {
        uploadImage: {
          server: '/api/upload',
          base64LimitSize: 5 * 1024 * 1024, // 5M 小于该值就插入 base64 格式（而不上传），默认为 0
          maxFileSize: 5 * 1024 * 1024, // 单个文件的最大体积限制，默认为 2M
          // 上传错误，或者触发 timeout 超时
          onError(file, err, res) {
            if (err.message.indexOf('exceeds maximum allowed size') > -1) {
              message.error('上传失败，图片不能超过5M')
            }
          }
        }
      }
    }

    // 组件销毁时，也及时销毁编辑器
    onBeforeUnmount(() => {
      const editor = editorRef.value
      if (editor == null) return
      editor.destroy()
    })
    const toolbarRefHeight = ref(40)
    onMounted(() => {
      nextTick(() => {
        setTimeout(() => {
          toolbarRefHeight.value = toolbarRef.value.$el.clientHeight + 1
        }, 10)
      })
    })

    const handleCreated = (editor) => {
      editorRef.value = editor // 记录 editor 实例，重要！
    }

    // 获取内容
    const getContent = () => {
      const editor = editorRef.value
      if (editor == null) return ''
      return editor.getHtml()
    }
    return {
      toolbarRef,
      themeType, editorRef, toolbarConfig, mode, valueHtml, toolbarRefHeight, editorConfig, handleCreated,
      getContent
    }
  }
})
</script>