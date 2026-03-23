<style lang="less">
</style>
<template>
  <n-alert type="error">
    {{ error }}
  </n-alert>
  <n-spin v-if="loading" />
</template>

<script>
import { defineComponent, ref, getCurrentInstance } from 'vue'
export default defineComponent({
  components: {},
  props: {
    dtsetId: String,
    type: String
  },
  setup(props) {
    const { proxy, ctx } = getCurrentInstance()
    const error = ref('')
    const loading = ref(false)

    const initData = () => {
      loading.value = true
      proxy.$api.get(`/knb/dataset/index/error/${props.dtsetId}/${props.type}`).then(res => {
        let entity = res.data || {}
        error.value = entity['errInf'] || '未知错误'
        loading.value = false
      }).catch(err => {
        console.error(err)
        loading.value = false
      })
    }
    initData()
    return {
      error, loading
    }
  }
})
</script>