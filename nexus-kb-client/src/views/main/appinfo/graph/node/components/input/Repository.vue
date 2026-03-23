<style lang="less">
</style>

<template>
  <n-select v-model:value="attr.attrVal" :options="reposList" filterable value-field="reposId" label-field="reposNm" size="small" :placeholder="`请选择${attr.attrLbl}`" />
</template>
<script>
  import { defineComponent, getCurrentInstance } from 'vue'
  import $api from '@/libs/axios'
  export default defineComponent({
    components: {
    },
    props: {
      attr: Object,
    },
    setup(props, context) {
      const reposList = ref([])
      const initReposList = () => {
        $api.post('/knb/repository/my/list').then(res => {
          reposList.value = res.data || []
        }).catch(err => {
          console.error(err)
        })
      }
      initReposList()
      return {
        reposList
      }
    }
  })
</script>
