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
    <n-form-item v-for="param in paramListForPrvd" :key="param.prmId" :label="param.prmNm" :path="param.prmCd">
      <n-input v-model:value="formData[param.prmCd]" :placeholder="`请输入${param.prmNm}`" />
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, getCurrentInstance, ref, computed } from 'vue'
import { isEmpty } from '@/libs/tools'

export default defineComponent({
  components: {
  },
  props: {
    prvd: Object
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const { prvdId } = props.prvd
    const formVm = ref()
    const formData = ref({})
    const formRules = ref({})

    const ecrpParamVals = ref({}) // 已经加密过的参数
    const ecrpParamIds = ref({})
    const initMyModelParamList = async () => {
      let res = await proxy.$api.post('/sys/model/param/my/list', { prvdId })
      let data = res['data']
      if (data) { // 有数据
        data.forEach(item => {
          let valEcrp = item.valEcrp === 'Y' // 是否已经被加密存储
          let prmCd = item.prmCd
          if (valEcrp) {
            ecrpParamVals.value[prmCd] = item.prmVal
          }
          ecrpParamIds.value[prmCd] = item.prmId
          formData.value[prmCd] = item.prmVal
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
      let list = llmPrvdParamList.value.filter(item => item.prmLvl === 'prvd' || item.prmLvl === 'both')
      list.forEach(param => {
        let required = param.notNull === 'Y'
        if (required) {
          formRules.value[param.prmCd] = [
            { required: true, message: `${param.prmNm}不能为空` }
          ]
        }
        if (formData.value[param.prmCd] === undefined) {
          let dftVal = param.dftVal || ''
          formData.value[param.prmCd] = dftVal
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
              if (value?.indexOf('*') > -1) { // regex.test(value)
                valEcrp = 'Y' // 已经被加密，后端不用再保存此参数值
              } else {
                valEcrp = 'N' // 没有被加密，后端需要加密保存
              }
            }
          }
          params.push({
            prmId: ecrpParamIds.value[prmCd],
            prvdId,
            modlId: null,
            userId: null,
            prmCd,
            prmVal: value,
            reqEcrp: param.reqEcrp, // 是否需要加密存储
            valEcrp
          })
        })
        return Promise.resolve(params)
      }
      return Promise.reject()
    }

    return {
      formVm,
      formData, formRules,
      paramListForPrvd,
      ok
    }
  }
})
</script>