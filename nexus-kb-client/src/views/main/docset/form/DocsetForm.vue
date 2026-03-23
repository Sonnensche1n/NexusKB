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
    <n-form-item label="名称" path="setNm">
      <n-input v-model:value="formData.setNm" placeholder="请输入文档集名称" />
    </n-form-item>
    <n-form-item label="介绍" path="setDesc">
      <n-input
        v-model:value="formData.setDesc"
        placeholder="请输入文档集介绍"
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
export default defineComponent({
  components: {
  },
  props: {
    /** 待修改的数据 */
    docset: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let docset = props['docset']
    if (!docset) {
      docset = {
        setId: '', setNm: '', setDesc: ''
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(docset)))
    const formRules = ref({
      setNm: [
        {
          required: true,
          message: '文档库名称必须填写',
          trigger: [ 'blur' ]
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
      formVm,
      formData, formRules,
      ok
    }
  }
})
</script>