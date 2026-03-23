<style lang="less">
.kb-markdown-view.md-editor {
  background-color: initial;
  .md-editor-preview-wrapper {
    padding: 0;
  }
  .md-editor-preview {
    background-color: initial;
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
  <MdPreview class="kb-markdown-view" :editorId="id" :modelValue="content" :theme="themeType" previewTheme="vuepress" codeTheme="github" />
</template>
<script>
import { defineComponent, getCurrentInstance, ref,  onBeforeUnmount, computed } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
import { random, localRead } from '@/libs/tools'
import EventBus from '@/libs/eventbus'
export default defineComponent({
  components: {
    MdPreview
  },
  props: {
    content: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const id = 'v' + random(true, 10, 32) // id 不能以数字开头
    const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE)
    const onThemeTypeChange = (type) => {
      themeType.value = type
    }
    EventBus.on('on-theme-type-change', onThemeTypeChange)
    onBeforeUnmount(() => {
      EventBus.off('on-theme-type-change', onThemeTypeChange)
    })
    return {
      id,
      themeType,
    }
  }
})
</script>