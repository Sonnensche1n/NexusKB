<style lang="less">
.kb-doc-editor {
  height: 100%;
  .header {
    text-align: center;
    font-size: 22px;
    font-weight: 600;
    padding: 20px;
  }
  .n-divider {
    margin-top: 0;
    margin-bottom: 0;
  }
  .content {
    height: calc(100% - 76px);
    padding: 20px;
  }
}
</style>
<template>
  <div class="kb-doc-editor">
    <div class="header">
      {{ docInfo.docTtl || '初始化中...' }}
    </div>
    <n-divider />
    <div class="content">
      <markdown ref="editorRef" v-if="docInfo.docTyp === 'md'" :content="docInfo.docCntnt" />
      <richtext ref="editorRef" v-else-if="docInfo.docTyp === 'rt'" :content="docInfo.docCntnt" />
    </div>
  </div>
</template>

<script>
import { defineComponent, getCurrentInstance, onBeforeUnmount, ref } from 'vue'
import EventBus from '@/libs/eventbus'
import Markdown from './editor/Markdown.vue'
import Richtext from './editor/Richtext.vue'

export default defineComponent({
  components: {
    Markdown, Richtext
  },
  props: {
    docId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const docId = props.docId
    const docInfo = ref({})
    const editorRef = ref(null)
    const initDocInfo = (id) => {
      proxy.$api.get('/doc/document/' + id).then(res => {
        if (!res.data.docCntnt) {
          res.data.docCntnt = ''
        }
        docInfo.value = res.data
      }).catch(err => {
        console.error(err)
      })
    }
    initDocInfo(docId)
    const saveContent = () => {
      const content = editorRef.value.getContent()
      return new Promise((resolve, reject) => {
        proxy.$api.put('/doc/document/content', { docId: docId, docCntnt: content }).then(res => {
          resolve(res)
        }).catch(err => {
          console.error(err)
          reject(err)
        })
      })
    }
    const onDocumentUpdate = (doc) => {
      if (doc.docId !== docId) {
        return
      }
      docInfo.value.docTtl = doc.docTtl
    }

    EventBus.on('on-document-update', onDocumentUpdate)
    onBeforeUnmount(() => {
      EventBus.off('on-document-update', onDocumentUpdate)
    })
    return {
      editorRef,
      docInfo, saveContent
    }
  }
})
</script>