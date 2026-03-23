<style lang="less">
</style>
<template>
  <n-alert type="warning" style="margin-top: 20px;">
    请选择需要重新构建索引的类型<br>
    摘要、Q&A、图谱等类型需要消耗额外的token
  </n-alert>
  <n-form
    ref="formVm"
    label-placement="left"
    label-width="auto"
    :model="formData"
    :rules="formRules"
    require-mark-placement="right-hanging"
    style="margin-top: 10px;"
  >
    <n-form-item label="" path="types">
      <n-checkbox-group v-model:value="formData.types">
        <n-space>
          <n-checkbox :value="option.value" v-for="option in options" :key="option.key" :disabled="disabledTypes.includes(option.value)">
            {{ option.label }}
          </n-checkbox>
        </n-space>
      </n-checkbox-group>
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { map2Options } from '@/libs/utils'
import { DATASET_INDEX_TYPE } from '@/libs/enum'

export default defineComponent({
  components: {},
  props: {
    dataset: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const formVm = ref()
    const formData = ref({
      types: []
    })
    const formRules = ref({
      types: [
        {
          required: true,
          type: 'array',
          message: '索引类型不能为空',
          trigger: 'change'
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
        return Promise.resolve(formData.value.types)
      }
      return Promise.reject()
    }

    let disabledTypes = []
    const dataset = props.dataset
    if (!(dataset.idxSts !== 'nobd' && dataset.idxSts !== 'new'))
      disabledTypes.push('index')
    if (!(dataset.prcsSts !== 'nobd' && dataset.prcsSts !== 'new'))
      disabledTypes.push('precis')
    if (!(dataset.qaSts !== 'nobd' && dataset.qaSts !== 'new'))
      disabledTypes.push('qanswer')
    if (!(dataset.tpltSts !== 'nobd' && dataset.tpltSts !== 'new'))
      disabledTypes.push('triplet')

    if (disabledTypes.length === 3) {
      formData.value.types.push('index')
    }
    return {
      formVm, formRules, formData,
      disabledTypes,
      options: map2Options(DATASET_INDEX_TYPE),
      ok
    }
  }
})
</script>