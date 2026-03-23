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
    <n-form-item label="名称" path="appNm">
      <n-input v-model:value="formData.appNm" placeholder="请输入应用名称" />
    </n-form-item>
    <n-form-item label="介绍" path="appIntd">
      <n-input
        v-model:value="formData.appIntd"
        placeholder="请输入应用介绍"
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
    app: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let app = props['app']
    if (!app) {
      app = {
        appId: '', appVer: 1, appNm: '', appIntd: '', appTyp: 'workflow', authRang: 'prvt'
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(app)))
    const formRules = ref({
      appNm: [
        {
          required: true,
          message: '应用名称必须填写',
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