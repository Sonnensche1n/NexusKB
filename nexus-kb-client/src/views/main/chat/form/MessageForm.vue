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
    <n-form-item label="" path="mesgCntnt">
      <n-input v-model:value="formData.mesgCntnt" type="textarea" placeholder="请输入消息内容" 
        :autosize="{
          minRows: 20,
          maxRows: 20,
        }"
      />
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import { NForm, NFormItem, NInput } from 'naive-ui'
export default defineComponent({
  components: {
    NForm, NFormItem, NInput
  },
  props: {
    /** 待修改的数据 */
    message: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    let message = props['message']
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(message)))
    const formRules = ref({
      mesgCntnt: [
        {
          required: true,
          message: '消息内容必须填写',
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