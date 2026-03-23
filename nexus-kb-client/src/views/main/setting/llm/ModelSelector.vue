<style lang="less">
.kb-model-selector {
  .n-cascader-submenu {
    width: auto !important;
  }
}
</style>

<template>
  <n-cascader class="kb-model-selector" clearable check-strategy="child"
    v-model:value="formData[valueKey]"
    placeholder="请选择模型"
    expand-trigger="hover"
    :to="false"
    :options="llmOptions"
    :disabled="disabled"
  />
</template>
<script>
  import { defineComponent, ref } from 'vue'
  import $api from '@/libs/axios'

  export default defineComponent({
    components: {
    },
    props: {
      formData: Object,
      valueKey: {
        type: String,
        default: 'llm'
      },
      modelType: {
        type: String,
        default: 'llm'
      },
      disabled: false
    },
    setup(props, context) {
      const llmOptions = ref([])
      const initLlmOptions = () => {
        $api.get('/sys/model/my/list').then(res => {
          let data = res.data || []
          data.forEach(prvd => {
            let children = []
            prvd['children']?.forEach(model => {
              model['disabled'] = model['type'] !== props.modelType
              if (model['disabled']) {
                return
              }
              children.push(model)
            })
            prvd['children'] = children
          })
          data = data.filter(prvd => prvd['children']?.length > 0)
          llmOptions.value = data
        }).catch(err => {
          console.error(err)
        })
      }
      initLlmOptions()
      return {
        llmOptions,
        initLlmOptions
      }
    }
  })
</script>
