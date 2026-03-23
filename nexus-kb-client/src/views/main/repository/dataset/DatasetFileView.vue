<style lang="less">
.kb-dataset-file-view {
  .n-drawer-header__main {
    display: flex;
    align-items: center;
  }
}
</style>
<template>
  <n-drawer class="kb-dataset-file-view" v-model:show="show" :show-mask="false" width="80%" resizable>
    <n-drawer-content closable body-content-style="padding: 0;">
      <template #header>
        <n-icon class="iconfont icon-eye" size="28px" />&nbsp;{{ title }}
      </template>
      <document-viewer v-if="docViewerId" :docId="docViewerId" />
      <file-viewer v-else :url="url" :type="type" />
    </n-drawer-content>
  </n-drawer>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import FileViewer from '@/components/custom/FileViewer.vue'
import DocumentViewer from '@/views/main/docset/form/DocumentViewer.vue'

export default defineComponent({
  components: {
    FileViewer, DocumentViewer
  },
  props: {
  },
  setup(props) {
    const show = ref(false)
    const title = ref('')
    const url = ref('')
    const type = ref('')

    const docViewerId = ref('')
    const toggle = ({dtsetNm, dtsetId, fileTyp, filePath, docId}) => {
      title.value = dtsetNm
      type.value = fileTyp
      docViewerId.value = docId
      if (fileTyp === 'link') {
        url.value = filePath
      } else {
        url.value = `/static/documents/${dtsetId}.${fileTyp}`
      }
      show.value = true
    }
    return {
      show, title, url, type, docViewerId,
      toggle
    }
  }
})
</script>