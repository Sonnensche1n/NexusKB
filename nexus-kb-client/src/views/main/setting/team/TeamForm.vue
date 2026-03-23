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
    <n-form-item label="名称" path="teamNm">
      <n-input v-model:value="formData.teamNm" placeholder="请输入团队名称" />
    </n-form-item>
    <n-form-item label="介绍" path="teamIntd">
      <n-input v-model:value="formData.teamIntd" type="textarea" placeholder="请输入团队介绍" />
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
    team: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let team = props['team']
    if (!team) {
      team = {
        teamId: '', teamNm: '', teamIntd: ''
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(team)))
    const formRules = ref({
      teamNm: [
        {
          required: true,
          message: '团队名称必须填写',
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