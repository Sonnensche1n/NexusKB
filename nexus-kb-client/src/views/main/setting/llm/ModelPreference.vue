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
    <n-form-item label="LLM" :path="formData.llm">
      <model-selector ref="modelRef" :formData="formData" valueKey="llm" />
    </n-form-item>
    <!-- <n-form-item label="Embedding" :path="formData['text-embedding']">
      <model-selector :formData="formData" valueKey="text-embedding" modelType="text-embedding" />
    </n-form-item> -->
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, ref, computed, watch } from 'vue'
import { SYSTEM_MODEL_PREFERENCE_PARAM_CODE } from '@/libs/enum'
import { isEmpty } from '@/libs/tools'
import ModelSelector from './ModelSelector.vue'

// 模型首选项
export default defineComponent({
  components: {
    ModelSelector
  },
  props: {
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const formVm = ref()
    let inited = false
    const formData = ref({
      prmId: '', llm: null, 'text-embedding': null
    })
    const formRules = ref({})

    const initFormData = () => {
      proxy.$api.get('/sys/setting/user/' + SYSTEM_MODEL_PREFERENCE_PARAM_CODE).then(res => {
        let data = res.data || {}
        let prmId = data['prmId']
        if (isEmpty(prmId)) {
          inited = true
          return
        }
        formData.value.prmId = prmId
        let emrts = data['prmEmrts'] || []
        emrts.forEach(emrt => {
          let valCd = emrt['valCd']
          let prmVal = emrt['prmVal'] || null
          if (valCd === 'llm') {
            formData.value.llm = prmVal
          } else if (valCd === 'text-embedding') {
            formData.value['text-embedding'] = prmVal
          }
        })
        setTimeout(() => {
          inited = true
        }, 100)
      }).catch(err => {
        console.error(err)
        err.msg = ''
        inited = true
      })
    }
    initFormData()

    const saveFormData = () => {
      let data = {
        prmId: formData.value.prmId,
        prmCd: SYSTEM_MODEL_PREFERENCE_PARAM_CODE,
        prmNm: '模型首选项',
        whthEmrt: 'Y',
        prmEmrts: [
          {
            prmId: formData.value.prmId,
            valCd: 'llm',
            prmCd: SYSTEM_MODEL_PREFERENCE_PARAM_CODE,
            prmVal: formData.value.llm,
            valOdr: 1
          },
          {
            prmId: formData.value.prmId,
            valCd: 'text-embedding',
            prmCd: SYSTEM_MODEL_PREFERENCE_PARAM_CODE,
            prmVal: formData.value['text-embedding'],
            valOdr: 2
          }
        ]
      }
      proxy.$api.post('/sys/setting/user', data).then(res => {
        let data = res.data || {}
        let prmId = data['prmId']
        formData.value.prmId = prmId // 因为这个因此不能watch整个对象
      }).catch(err => {
        console.error(err)
      })
    }

    watch(() => formData.value.llm, () => {
      if (inited) {
        saveFormData()
      }
    })
    watch(() => formData.value['text-embedding'], () => {
      if (inited) {
        saveFormData()
      }
    })

    const modelRef = ref()

    const resetSelector = () => {
      modelRef.value.initLlmOptions()
    }
    return {
      modelRef,
      formVm, formData, formRules,
      resetSelector
    }
  }
})
</script>