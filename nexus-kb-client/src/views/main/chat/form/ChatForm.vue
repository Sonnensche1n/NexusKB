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
    <n-form-item label="标题" path="chatTtl">
      <n-input v-model:value="formData.chatTtl" placeholder="请输入会话标题" />
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
    chat: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let chat = props['chat']
    if (!chat) {
      chat = {
        chatId: '', reposId: '', chatTtl: ''
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(chat)))
    const formRules = ref({
      chatTtl: [
        {
          required: true,
          message: '会话标题必须填写',
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