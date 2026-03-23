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
    <n-form-item label="名称" path="ctlgNm">
      <n-input v-model:value="formData.ctlgNm" placeholder="请输入目录名称" />
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
export default defineComponent({
  components: {},
  props: {
    /** 待修改的数据 */
    catalog: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let catalog = props['catalog']
    if (!catalog) {
      catalog = {
        ctlgId: '', ctlgNm: ''
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(catalog)))
    const formRules = ref({
      ctlgNm: [
        {
          required: true,
          message: '目录名称必须填写',
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