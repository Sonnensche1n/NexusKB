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
    <n-form-item label="主语" path="tpltSbjct">
      <n-input v-model:value="formData.tpltSbjct" placeholder="请输入主语" />
    </n-form-item>
    <n-form-item label="谓语" path="tpltPrdct">
      <n-input v-model:value="formData.tpltPrdct" placeholder="请输入谓语" />
    </n-form-item>
    <n-form-item label="宾语" path="tpltObjct">
      <n-input v-model:value="formData.tpltObjct" placeholder="请输入宾语" />
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, inject, ref } from 'vue'
import { useCatalog } from './mixin/catalog'
export default defineComponent({
  components: {},
  props: {
    /** 待修改的数据 */
    triplet: {
      type: Object,
      default: null
    }
  },
  setup(props) {
    let triplet = props['triplet']
    if (!triplet) {
      triplet = {
        tpltId: '', reposId: '', dtsetId: '', tpltSeq: null, tpltSbjct: '', tpltPrdct: '', tpltObjct: '', tpltSrc: ''
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(triplet)))
    formData.value.tpltSrc = 'hm'
    const formRules = ref({
      tpltSbjct: [{ required: true, message: '主语必须填写', trigger: [ 'blur' ] }],
      tpltPrdct: [{ required: true, message: '谓语必须填写', trigger: [ 'blur' ] }],
      tpltObjct: [{ required: true, message: '宾语必须填写', trigger: [ 'blur' ] }]
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