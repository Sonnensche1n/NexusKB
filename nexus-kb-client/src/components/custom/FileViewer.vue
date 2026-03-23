<style lang="less">
.kb-doc-view {
  width: 100%;
  height: 100%;
  position: relative;
  &-iframe {
    width: 100%;
    height: 100%;
    border: none;
    overflow: hidden;
    iframe {
      width: 100%;
      height: 100%;
      border-width: 0;
    }
  }
  .n-spin-body {
    position: absolute;
    width: 100%;
    top: 10px;
  }
}
</style>

<template>
  <div class="kb-doc-view">
    <div class="kb-doc-view-iframe" v-if="iframeTypes.includes(type)">
      <iframe :src="url" @load="onSucceed" @error="onFailed"></iframe>
    </div>
    <vue-office-docx v-else-if="docxTypes.includes(type)" :src="url" @rendered="onSucceed" @error="onFailed" />
    <n-alert v-else type="warning" style="margin: 10px;">
      该文件类型暂不支持预览！
    </n-alert>
    <n-spin v-if="loading" />
  </div>
</template>
<script>
  import { defineComponent } from 'vue'
  import VueOfficeDocx from '@vue-office/docx'
  
  export default defineComponent({
    components: {
      VueOfficeDocx
    },
    props: {
      url: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      }
    },
    setup(props) {
      const loading = ref(true)
      const iframeTypes = ['pdf', 'html', 'txt', 'md', 'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'mp3', 'wav', 'ogg', 'flac', 'link' ]
      const docxTypes = ['docx', 'doc']
      
      const onSucceed = () => {
        loading.value = false
      }
      const onFailed = () => {
        loading.value = false
      }
      return {
        loading, iframeTypes, docxTypes,
        onSucceed, onFailed
      }
    }
  })
</script>
