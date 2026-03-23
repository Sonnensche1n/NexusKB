<style lang="less">
</style>
<template>
  <n-form
    ref="formVm"
    label-placement="top"
    label-width="auto"
    :model="formData"
    :rules="formRules"
    require-mark-placement="right-hanging"
    style="margin-top: 10px;"
  >
    <n-form-item label="模型类型" path="modlTyp">
      <n-radio-group v-model:value="formData['modlTyp']" name="radiogroup" :disabled="isEdit">
        <n-radio-button v-for="typ in modelTypeOptions" :key="typ.value" :value="typ.value">
          {{ typ.label }}
        </n-radio-button>
      </n-radio-group>
    </n-form-item>
    <n-form-item label="模型名称" path="modlNm">
      <n-input v-model:value="formData['modlNm']" :placeholder="`请输入模型名称`" :disabled="isEdit" />
    </n-form-item>
    <n-form-item v-for="param in paramListForPrvd" :key="param.prmId" :label="param.prmNm" :path="param.prmCd">
      <n-input v-model:value="formData[param.prmCd]" :placeholder="`请输入${param.prmNm}`" />
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, ref, computed } from 'vue'
import { isEmpty } from '@/libs/tools'
import { LLM_MODEL_TYPE } from '@/libs/enum'
import { map2Options } from '@/libs/utils'

export default defineComponent({
  components: {
  },
  props: {
    prvd: Object,
    model: Object
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const { prvdId, modlTyp } = props.prvd
    const model = props.model || {}
    const modlId = model.modlId
    const isEdit = !isEmpty(modlId)
    const formVm = ref()
    const modelTypeOptions = map2Options(LLM_MODEL_TYPE).filter(option => modlTyp.indexOf(option.value) > -1)
    const formData = ref({
      modlNm: model.modlNm,
      modlTyp: model.modlTyp || modelTypeOptions[0].value
    })
    const formRules = ref({
      modlTyp: [
        { required: true, message: '模型类型不能为空' }
      ],
      modlNm: [
        { required: true, message: '模型名称不能为空' }
      ]
    })

    const ecrpParamVals = ref({}) // 已经加密过的参数
    const ecrpParamIds = ref({})
    const initMyModelParamList = async () => {
      let res = await proxy.$api.post('/sys/model/param/my/list', { prvdId, modlId })
      let data = res['data']
      if (data) { // 有数据
        data.forEach(item => {
          let valEcrp = item.valEcrp === 'Y' // 是否已经被加密存储
          let prmCd = item.prmCd
          if (valEcrp) {
            ecrpParamVals.value[prmCd] = item.prmVal
          }
          ecrpParamIds.value[prmCd] = item.prmId
          formData.value[item.prmCd] = item.prmVal
        })
      }
    }
    initMyModelParamList()
    const llmPrvdParamList = ref([])
    const initLlmPrvdParamList = () => {
      proxy.$api.get('/sys/model/prvd/param/list/' + prvdId).then(res => {
        llmPrvdParamList.value = res.data || []
      }).catch(err => {
        console.error(err)
      })
    }
    initLlmPrvdParamList()
    const paramListForPrvd = computed(() => {
      let list = llmPrvdParamList.value.filter(item => item.prmLvl === 'modl' || item.prmLvl === 'both')
      list.forEach(param => {
        let required = param.notNull === 'Y'
        if (required) {
          formRules.value[param.prmCd] = [
            { required: true, message: `${param.prmNm}不能为空` }
          ]
        }
        if (!isEdit) {
          if (formData.value[param.prmCd] === undefined) {
            let dftVal = param.dftVal || ''
            formData.value[param.prmCd] = dftVal
          }
        }
      })
      return list
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
        let params = []
        let regex = /^[a-zA-Z-_0-9]{6}\*+[a-zA-Z0-9]{2}/
        paramListForPrvd.value.forEach(param => {
          let prmCd = param.prmCd
          let oldEcrpVal = ecrpParamVals.value[prmCd]
          let value = formData.value[prmCd]
          let valEcrp = 'N'
          if (oldEcrpVal) { // 有旧的加密值，比较是否没有变动过
            if (value === oldEcrpVal) { // 没有变动过，后端不用加密
              valEcrp = 'Y' // 已经被加密，后端不用再保存此参数值
            } else { // 判断值是否带 * 号，前面6个字符后面两个字符，中间全是* 号
              if (regex.test(value)) {
                valEcrp = 'Y' // 已经被加密，后端不用再保存此参数值
              } else {
                valEcrp = 'N' // 没有被加密，后端需要加密保存
              }
            }
          }
          params.push({
            prmId: ecrpParamIds.value[prmCd],
            prvdId,
            modlId,
            userId: null,
            prmCd: param.prmCd,
            prmVal: formData.value[param.prmCd],
            reqEcrp: param.reqEcrp, // 是否需要加密存储
            valEcrp
          })
        })
        let model = {
          modlId,
          prvdId,
          userId: null,
          modlNm: formData.value['modlNm'],
          modlTyp: formData.value['modlTyp']
        }
        return Promise.resolve({
          model, params
        })
      }
      return Promise.reject()
    }

    return {
      isEdit,
      formVm, modelTypeOptions,
      formData, formRules,
      paramListForPrvd,
      ok
    }
  }
})
</script>