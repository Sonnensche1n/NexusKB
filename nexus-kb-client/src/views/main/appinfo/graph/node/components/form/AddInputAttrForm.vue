<style lang="less">
.kb-node-attr-form {
  .n-form-item.options {
    .n-form-item-blank {
      display: flex;
      flex-direction: column;
      gap: 10px;
      .n-button {
        width: 100%;
      }
    }
  }
}
</style>
<template>
  <n-form class="kb-node-attr-form"
    ref="formVm"
    label-placement="left"
    label-width="auto"
    :model="formData"
    :rules="formRules"
    require-mark-placement="right-hanging"
  >
    <n-form-item label="数据类型" path="dataTyp">
      <n-radio-group v-model:value="formData.dataTyp">
        <n-radio-button v-for="dataTyp in dataTypOptions" :key="dataTyp.value" :value="dataTyp.value" :title="dataTyp.label">
          <n-icon :class="dataTyp.icon" />
        </n-radio-button>
      </n-radio-group>
    </n-form-item>
    <n-form-item label="变量名称" path="attrKey">
      <n-input v-model:value="formData.attrKey" placeholder="请输入变量名称" />
    </n-form-item>
    <n-form-item label="显示名称" path="attrLbl">
      <n-input v-model:value="formData.attrLbl" placeholder="请输入显示名称" />
    </n-form-item>
    <n-form-item label="最大长度" path="maxLth" v-if="formData.dataTyp === 'string'">
      <n-input-number v-model:value="formData.maxLth" :min="1" :max="200" placeholder="请输入最大长度" style="width: 100%;" />
    </n-form-item>
    <n-form-item label="是否必填" path="notNull">
      <n-switch v-model:value="formData.notNull" checked-value="Y" unchecked-value="N" />
    </n-form-item>
    <n-form-item label="下拉选项" path="options" v-if="formData.dataTyp === 'selection'" class="options">
      <n-input v-model:value="formData.options" style="display: none;" />
      <n-input v-for="(option, index) in selectOptions" :default-value="option" :key="`${option}-${index}`" :on-update:value="value => selectOptions[index] = value" type="text" placeholder="请输入下拉选项">
        <template #suffix>
          <n-button size="small" text type="error">
            <n-icon class="iconfont icon-delete" @click="selectOptions.splice(index, 1)" />
          </n-button>
        </template>
      </n-input>
      <n-button @click="selectOptions.push('')"><n-icon class="iconfont icon-plus"/>&nbsp;添加</n-button>
    </n-form-item>
  </n-form>
</template>

<script>
import { defineComponent, watch, ref, computed } from 'vue'
import { uuid, isEmpty } from '@/libs/tools'
import { NODE_ATTR_VALUE_DATA_TYPE } from '@/libs/enum'
export default defineComponent({
  components: {
  },
  props: {
  },
  setup(props) {
    const dataTypOptions = ref([])
    for (let key in NODE_ATTR_VALUE_DATA_TYPE) {
      dataTypOptions.value.push(NODE_ATTR_VALUE_DATA_TYPE[key])
    }

    const formVm = ref()
    const formData = ref({
      // { attrId: 'start_question', ndfId: 'start', attrCls: 'opt', attrKey: 'question', attrLbl: '用户问题', dataTyp: 'string', attrDesc: '', attrSrc: 'aut', notNull: 'Y', dftVal: '', compTyp: 'textarea' } // compTyp 前端组件: input,textarea,number,select,repostory知识库选择器,llm模型选择器,variable变量选择器,classify分类输入框 等等
      attrId: uuid(), ndfId: '', nodeId: '', attrCls: 'ipt', attrKey: '', attrLbl: '', maxLth: 50, notNull: 'Y', dataTyp: 'string', attrDesc: '', attrSrc: 'ipt,var', valSrc: 'aut', dftVal: '', compTyp: 'input', options: '', builtIn: 'N' // options 下拉框的可选值
    })
    const selectOptions = ref([])
    watch(selectOptions, (options) => {
      let fs = options.filter(option => !isEmpty(option))
      if (fs.length === 0) {
        return
      }
      formData.value.options = options.join(',')
    }, {
      deep: true
    })
    watch(() => formData.value.dataTyp, (dataTyp) => {
      let attrSrc = 'ipt,var' //, valSrc = 'ipt'
      if (dataTyp === 'selection') {
        formData.value.compTyp = 'select'
        attrSrc = 'slt,var'
        // valSrc = 'slt'
      } else if (dataTyp === 'number') {
        formData.value.compTyp = 'number'
      } else if (dataTyp === 'text') {
        formData.value.compTyp = 'textarea'
      } else {
        formData.value.compTyp = 'input'
      }
      formData.value.attrSrc = attrSrc
      // formData.value.valSrc = valSrc
    })
    const formRules = computed(() => {
      return {
        attrKey: [{ required: true, message: '变量名称必须填写', trigger: 'blur' }],
        attrLbl: [{ required: true, message: '显示名称必须填写', trigger: 'blur' }],
        maxLth: [{ required: formData.value.dataTyp === 'string', type: 'number', message: '最大长度必须填写', trigger: 'blur' }],
        options: [{ required: formData.value.dataTyp === 'selection', message: '下拉选项必须填写', trigger: 'blur' }],
      }
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
      dataTypOptions,
      formVm,
      formData, formRules, selectOptions,
      ok
    }
  }
})
</script>