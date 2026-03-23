<style lang="less">
.kb-doc-viewer {
  .header {
    text-align: center;
    padding: 20px;
    position: relative;
    .title {
      font-size: 22px;
      font-weight: 600;
    }
    .time {
      position: absolute;
      left: 0;
      bottom: 0;
      font-size: 12px;
      width: 100%;
      display: block;
      color: var(--border-color);
    }
  }
  .n-divider {
    margin-top: 0;
    margin-bottom: 0;
  }
  .content {
    padding: 20px;
  }
  .skeleton {
    padding: 0 20px;
    position: absolute;
    width: 100%;
    left: 0;
    margin-top: -20px;
  }
}
</style>
<template>
  <n-scrollbar class="kb-doc-viewer" :id="`d${docId}`">
    <div class="header">
      <span class="title">{{ docInfo.docTtl || '初始化中...' }}</span>
      <span class="time" v-if="docInfo.updTm"><n-time :time="new Date()" :to="new Date(docInfo.updTm)" type="relative" /></span>
    </div>
    <n-divider />
    <div class="content">
      <markdown v-if="docInfo.docTyp === 'md'" :content="docInfo.docCntnt" />
      <richtext v-else-if="docInfo.docTyp === 'rt'" :content="docInfo.docCntnt" />
    </div>
    <div class="skeleton" v-if="loading">
      <n-skeleton text :repeat="5" />
      <n-skeleton text style="width: 50%" />
    </div>
    <n-empty v-if="!loading && !docInfo.docCntnt" description="没有内容"/>
    <n-back-top :to="`#d${docId}`" :right="24" :bottom="32" />
  </n-scrollbar>
</template>

<script>
import { defineComponent, getCurrentInstance, onBeforeUnmount, ref } from 'vue'
import EventBus from '@/libs/eventbus'
import Markdown from './viewer/Markdown.vue'
import Richtext from './viewer/Richtext.vue'
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
  setup(props, context) {
    const { proxy, ctx } = getCurrentInstance()
    const docId = props.docId
    const docInfo = ref({})
    const loading = ref(false)
    const initDocInfo = (id) => {
      loading.value = true
      proxy.$api.get('/doc/document/' + id).then(res => {
        if (!res.data?.docCntnt) {
          res.data.docCntnt = ''
          context.emit('on-empty-content')
        }
        docInfo.value = res.data
        loading.value = false
      }).catch(err => {
        console.error(err)
        loading.value = false
      })
    }
    initDocInfo(docId)

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
      docInfo, loading
    }
  }
})
</script>