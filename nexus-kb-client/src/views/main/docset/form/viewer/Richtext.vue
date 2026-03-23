<style lang="less">
// @import 'highlight.js/styles/stackoverflow-light.css';
@import 'styles/stackoverflow-light.less';
@import 'styles/stackoverflow-dark.less';
.kb-richtext-view {
  p, li {
    white-space: pre-wrap; /* 保留空格 */
  }
  p {
    margin: 15px 0;
  }
  blockquote {
    border-left: 8px solid var(--primary-color);
    padding: 10px 10px;
    margin: 10px 0;
    background-color: var(--divider-color);
  }
  code {
    font-family: monospace;
  }
  pre>code {
    display: block;
    padding: 10px;
    margin: .5em 0;
    padding: 1em;
    background-color: #F8F8F8;
    border-color: var(--border-color);
    border-radius: var(--border-radius);
  }
  table {
    border-collapse: collapse;
  }
  td, th {
    border: 1px solid var(--border-color);
    min-width: 50px;
    height: 20px;
  }
  th {
    background-color: #f1f1f1;
  }
  ul, ol {
    padding-left: 20px;
  }
  input[type="checkbox"] {
    margin-right: 5px;
  }
}

.kb-richtext-view.dark {
  code {
    background-color: #1A1A1A;
  }
}
</style>
<template>
  <div :id="id" :class="`kb-richtext-view kb-code ${themeType}`" v-html="content"></div>
</template>

<script>
import { defineComponent, ref, onBeforeUnmount, computed, onMounted, nextTick } from 'vue'
import hljs from 'highlight.js'
import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
import { random, localRead } from '@/libs/tools'
import EventBus from '@/libs/eventbus'
export default defineComponent({
  components: {
  },
  props: {
    content: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE)
    const onThemeTypeChange = (type) => {
      themeType.value = type
    }
    EventBus.on('on-theme-type-change', onThemeTypeChange)
    onBeforeUnmount(() => {
      EventBus.off('on-theme-type-change', onThemeTypeChange)
    })

    const id = 'rt' + random(true, 10, 32) // id 不能以数字开头
    onMounted(() => {
      nextTick(() => {
        document.getElementById(id).querySelectorAll('pre code').forEach(element => {
          hljs.highlightElement(element)
        })
      })
    })
    return {
      id,
      themeType
    }
  }
})
</script>