<template>
  <div style="display: none;"></div>
</template>
<script>
  import { defineComponent } from 'vue'
  import { useMessage } from 'naive-ui'
  
  export default defineComponent({
    components: {
    },
    setup() {
      window.$message = useMessage()
      return {}
    }
  })
</script>
