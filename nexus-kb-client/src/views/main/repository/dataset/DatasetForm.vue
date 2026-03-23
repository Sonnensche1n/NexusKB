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
    <n-form-item label="名称" path="dtsetNm">
      <n-input v-model:value="formData.dtsetNm" placeholder="请输入数据集名称" />
    </n-form-item>
    <n-form-item label="目录" path="ctlgId">
      <n-tree-select
        v-model:value="formData.ctlgId"
        placeholder="请选择目录"
        :options="treeData"
        filterable
        key-field="ctlgId"
        label-field="ctlgNm"
      />
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
    dataset: {
      type: Object,
      default: null
    },
    reposId: String
  },
  setup(props) {
    const { treeData, renderTreeItemIcon } = useCatalog()
    let dataset = props['dataset']
    if (!dataset) {
      dataset = {
        dtsetId: '', dtsetNm: '', ctlgId: ''
      }
    } else {
      if (!dataset['ctlgId']) {
        dataset['ctlgId'] = ''
      }
    }
    const formVm = ref()
    const formData = ref(JSON.parse(JSON.stringify(dataset)))
    const formRules = ref({
      dtsetNm: [
        {
          required: true,
          message: '数据集名称必须填写',
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
      formData, formRules, treeData,
      renderTreeItemIcon,
      ok
    }
  }
})
</script>