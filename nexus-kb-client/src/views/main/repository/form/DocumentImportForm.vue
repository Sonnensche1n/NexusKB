<style lang="less">
</style>
<template>
  <n-upload
    ref="uploadRef"
    multiple
    :action="`${baseURL}/knb/dataset/upload/document`"
    accept=".pdf,.docx,.txt,.ppt,.pptx,.md"
    :file-list="fileList"
    :default-upload="false"
    :headers="{
      'token': token
    }"
    :data="{
      reposId: reposId,
      ctlgId: catalogId
    }"
    :max="10"
    :on-update:file-list="onFileListUpdate"
    :on-finish="onUploadFinish"
    :on-error="onUploadError"
  >
    <n-upload-dragger>
      <div style="margin-bottom: 12px">
        <n-icon size="48" :depth="3" class="iconfont icon-cloudupload"></n-icon>
      </div>
      <n-text style="font-size: 14px">
        点击或者拖动文件到该区域来上传
        <br>
        文本支持上传PDF、DOCX、TXT、PPTX、MD文件
        <br>
        [不支持扫描版PDF]
      </n-text>
    </n-upload-dragger>
  </n-upload>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import { } from 'naive-ui'
import useUserStore from '@/store/user'
import { baseURL } from '@/config'
export default defineComponent({
  components: {
  },
  props: {
    reposId: {
      type: String,
      required: true
    },
    catalogId: {
      type: String
    }
  },
  setup(props) {
    const uploadRef = ref()
    const fileList = ref([])
    const finishCount = ref(0)
    const errorCount = ref(0)
    const onFileListUpdate = (list) => {
      fileList.value = list
    }
    const onUploadFinish = () => {
      finishCount.value++
    }
    const onUploadError = () => {
      errorCount.value++
    }
    const onSubmit = () => {
      uploadRef.value.submit()
      return new Promise((resolve, reject) => {
        let timer = setInterval(() => {
          if (finishCount.value + errorCount.value === fileList.value.length) {
            clearInterval(timer)
            if (errorCount.value === 0) {
              resolve()
            } else {
              reject()
            }
          }
        }, 500)
      })
    }
    const ok = async () => {
      if (fileList.value.length === 0) {
        return
      }
      await onSubmit()
      return true
    }
    return {
      baseURL,
      uploadRef,
      fileList,
      reposId: props.reposId,
      catalogId: props.catalogId,
      token: useUserStore().getToken,
      onUploadFinish, onUploadError, onFileListUpdate,
      ok
    }
  }
})
</script>