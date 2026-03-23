<style lang="less">
.kb-resource-rela {
  display: flex;
  padding: 24px 0;
  .n-select:first-child {
    .n-base-selection {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
  }
  .n-select:last-child {
    margin-left: -1px;
    .n-base-selection {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
  }
}
</style>

<template>
  <div class="kb-resource-rela">
    <n-select
      v-model:value="selectedCoppls"
      multiple
      filterable
      placeholder="输入用户昵称搜索"
      label-field="nkNm"
      value-field="userId"
      :options="copplOptions"
      :loading="loading"
      clearable
      remote
      :clear-filter-after-select="true"
      @search="onSearch"
    />
  </div>
</template>
<script>
  import { defineComponent, ref, reactive, getCurrentInstance, h } from 'vue'
  import { useDialog } from 'naive-ui'
  import { isEmpty } from '@/libs/tools'
  import _ from 'lodash'
  export default defineComponent({
    components: {
    },
    props: {
      rscId: {
        type: String,
        required: true
      },
      rscTyp: {
        type: String,
        required: true
      }
    },
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const rscId = props.rscId
      const rscTyp = props.rscTyp
      const dialog = useDialog()
      const loading = ref(false)
      const copplOptions = ref([])
      const selectedCoppls = ref([])
      const selectedAuth = ref('alter')
      const onSearch = _.debounce((query) => {
        if (isEmpty(query)) {
          return
        }
        loading.value = true
        proxy.$api.post('/sys/resource/unreled/coppl/list', {
          rscId, nkNm: query
        }).then(res => {
          copplOptions.value = res.data || []
          loading.value = false
        }).catch(err => {
          console.error(err)
          loading.value = false
        })
      }, 500)
      const ok = () => {
        if (selectedCoppls.value.length === 0) {
          return
        }
        let reposCoppls = []
        selectedCoppls.value.forEach(userId => {
          reposCoppls.push({
            userId,
            rscId,
            rscTyp,
            coAuth: selectedAuth.value
          })
        })
        return reposCoppls
      }
      return {
        loading, selectedCoppls, copplOptions,
        onSearch, ok
      }
    }
  })
</script>
