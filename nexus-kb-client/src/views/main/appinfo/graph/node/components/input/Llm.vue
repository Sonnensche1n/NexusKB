<style lang="less">
</style>

<template>
  <n-cascader class="kb-flow-node-variable" size="small" clearable check-strategy="child"
    v-model:value="attr.attrVal"
    placeholder="请选择模型"
    expand-trigger="hover"
    :options="llmOptions"
  />
</template>
<script>
  import { defineComponent, ref } from 'vue'
  import $api from '@/libs/axios'

  export default defineComponent({
    components: {
    },
    props: {
      attr: Object,
    },
    setup(props, context) {
      let attr = props['attr']
      const llmOptions = ref([])
      const initLlmOptions = () => {
        $api.get('/sys/model/my/list').then(res => {
          llmOptions.value = res.data || []
        }).catch(err => {
          console.error(err)
        })
      }
      initLlmOptions()
      return {
        llmOptions
      }
    }
  })
</script>
