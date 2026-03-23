<style lang="less">
</style>
<template>
  <n-form
    ref="formVm"
    label-placement="left"
    label-width="auto"
    :model="formData"
    :rules="formRules"
    require-mark-placement="right-hanging"
  >
    <n-form-item label="名称" path="reposNm">
      <n-input v-model:value="formData.reposNm" placeholder="请输入知识库名称" />
    </n-form-item>
    <n-form-item label="索引" path="vecModlId">
      <model-selector :formData="formData" valueKey="vecModlId" modelType="text-embedding" :disabled="isEdit"/>
    </n-form-item>
    <n-form-item label="介绍" path="reposDesc">
      <n-input
        v-model:value="formData.reposDesc"
        placeholder="请输入知识库介绍"
        type="textarea"
        :autosize="{
          minRows: 3,
          maxRows: 5
        }"
      />
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import { isEmpty } from '@/libs/tools'
import ModelSelector from '@/views/main/setting/llm/ModelSelector.vue'
export default defineComponent({
  components: {
    ModelSelector
  },
  props: {
    /** 待修改的数据 */
    repository: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let repository = props['repository']
    let isEdit = false
    if (!repository) {
      repository = {
        reposId: '', reposNm: '', vecModlId: 'default/m3e-small', reposDesc: ''
      }
    } else {
      if (isEmpty(repository['vecModlId'])) {
        repository['vecModlId'] = 'default/m3e-small'
      }
      isEdit = true
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(repository)))
    const formRules = ref({
      reposNm: [
        {
          required: true,
          message: '知识库名称必须填写',
          trigger: [ 'blur' ]
        }
      ],
      vecModlId: [
        {
          required: true,
          message: '请选择构建索引的模型',
          trigger: [ 'change' ]
        }
      ]
    })
    const validate = () => {
      return formVm.value.validate()
    }
    const ok = async () => {
      let valid = false
      try {
        await validate()
        valid = true
      } catch (err) {
        // 具体的错误信息项 err
        console.error(err)
      }
      if (valid) {
        return Promise.resolve(formData.value)
      }
      return Promise.reject()
    }
    
    return {
      isEdit,
      formVm,
      formData, formRules,
      ok
    }
  }
})
</script>