<style lang="less">
.kb-qa-form.n-grid {
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
  <n-grid class="kb-qa-form" x-gap="12" :cols="2">
    <n-gi class="grid-column">
      <p class="title">问题</p>
      <n-input v-model:value="formData.qstQuest" placeholder="请输入问题" type="textarea" size="small"
        :autosize="{
          minRows: 25,
          maxRows: 25,
        }"
      />
    </n-gi>
    <n-gi class="grid-column">
      <p class="title">答案</p>
      <n-input v-model:value="formData.qstAswr" placeholder="请输入答案" type="textarea" size="small" :maxlength="4500"
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
    quest: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let quest = props['quest']
    if (!quest) {
      quest = {
        qstId: '', reposId: '', dtsetId: '', qstQuest: '', qstAswr: '', qstSrc: 'hm'
      }
    }
    const formData = ref(JSON.parse(JSON.stringify(quest)))
    const validate = () => {
      if (isEmpty(formData.value.qstQuest) || isEmpty(formData.value.qstAswr)) {
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