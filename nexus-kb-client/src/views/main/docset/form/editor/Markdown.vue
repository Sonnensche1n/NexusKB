<style lang="less">
.kb-markdown-edit.md-editor {
  background-color: var(--base-color);
  height: 100%;
  .md-editor-preview-wrapper {
    padding: 0 0 0 2px;
  }
  .md-editor-preview {
    background-color: var(--base-color);
    font-size: var(--font-size);
    p {
      margin: 0;
    }
    p,h1,h2,h3,h4,h5 {
      color: var(--text-color-base);
    }
  }
}
</style>
<template>
  <md-editor class="kb-markdown-edit" v-model="text" :theme="themeType" :toolbarsExclude="toolbarsExclude" @onUploadImg="onUploadImg" previewTheme="vuepress" codeTheme="github" />
</template>
<script>
import { defineComponent, getCurrentInstance, ref,  onBeforeUnmount, computed } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
import { random, localRead } from '@/libs/tools'
import EventBus from '@/libs/eventbus'
export default defineComponent({
  components: {
    MdEditor
  },
  props: {
    content: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const text = ref(props.content)
    const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE)
    const onThemeTypeChange = (type) => {
      themeType.value = type
    }
    EventBus.on('on-theme-type-change', onThemeTypeChange)
    onBeforeUnmount(() => {
      EventBus.off('on-theme-type-change', onThemeTypeChange)
    })

    const toolbarsExclude = [
      'save', 'fullscreen', 'github', 'link'
    ]

    // 获取内容
    const getContent = () => {
      return text.value
    }
    
    const onUploadImg = async (files, callback) => {
      const res = await Promise.all(
        files.map((file) => {
          return new Promise((resolve, reject) => {
            const form = new FormData();
            form.append('file', file);
            proxy.$api.post('/sys/file/upload', form, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            .then((res) => resolve(res))
            .catch((error) => reject(error))
          })
        })
      )
      callback(res.map((item) => item.data.fileUrl))
    }

    return {
      text,
      themeType,
      toolbarsExclude,
      getContent, onUploadImg
    }
  }
})
</script>