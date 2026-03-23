<style lang="less">
.kb-precis-form.n-grid {
  .grid-column {
    p.title {
      height: 24px;
      line-height: 24px;
      font-weight: 550;
      margin: 10px 0;
    }
  }
  .grid-column:first-child {
    .title::before {
      content: '*';
      color: var(--error-color);
      margin-right: 4px;
      position: relative;
      top: 2px;
    }
  }
}
</style>
<template>
  <n-grid class="kb-precis-form" x-gap="12" :cols="1">
    <n-gi class="grid-column">
      <p class="title">摘要内容</p>
      <n-input v-model:value="formData.prcsCntnt" placeholder="请输入摘要内容" type="textarea" size="small"
        :autosize="{
          minRows: 25,
          maxRows: 25,
        }"
      />
    </n-gi>
  </n-grid>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import { NForm, NFormItem, NInput } from 'naive-ui'
import { isEmpty } from '@/libs/tools'
export default defineComponent({
  components: {
    NForm, NFormItem, NInput
  },
  props: {
    /** 待修改的数据 */
    precis: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let precis = props['precis']
    if (!precis) {
      precis = {
        prcsId: '', dtsetId: '', reposId: '', prcsSeq: null, prcsCntnt: ''
      }
    }
    const formData = ref(JSON.parse(JSON.stringify(precis)))
    const validate = () => {
      if (isEmpty(formData.value.prcsCntnt)) {
        return false
      }
      return true
    }
    const ok = async () => {
      let valid = validate()
      if (valid) {
        return Promise.resolve(formData.value)
      }
      return Promise.reject()
    }
    
    return {
      formData,
      ok
    }
  }
})
</script>