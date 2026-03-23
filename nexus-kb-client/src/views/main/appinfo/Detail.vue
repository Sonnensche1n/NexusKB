<style lang="less">
.kb-appinfo-detail {
  height: 100%;
}
</style>

<template>
  <div class="kb-appinfo-detail">
    <workflow :appId="appId" />
  </div>
</template>
<script>
  import { defineComponent, ref, watch, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import Workflow from './Workflow.vue'

  export default defineComponent({
    components: {
      Workflow
    },
    setup() {
      const route = useRoute()
      return {
        appId: route.query.id
      }
    }
  })
</script>
