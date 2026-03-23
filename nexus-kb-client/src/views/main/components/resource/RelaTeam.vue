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
      v-model:value="selectedTeams"
      multiple
      filterable
      placeholder="输入团队名称搜索"
      label-field="teamNm"
      value-field="teamId"
      :options="teamOptions"
      :loading="loading"
      clearable
      remote
      :clear-filter-after-select="true"
      @search="onSearchTeam"
    />
    <n-select v-model:value="selectedAuth" :options="authOptions" style="width: 120px;" />
  </div>
</template>
<script>
  import { defineComponent, ref, reactive, getCurrentInstance, h } from 'vue'
  import { NTag, NBadge, useDialog } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, map2Options } from '@/libs/utils'
  import { isEmpty } from '@/libs/tools'
  import { COMMON_AUTH_OPTION_TYPE } from '@/libs/enum'
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
      const teamOptions = ref([])
      const selectedTeams = ref([])
      const selectedAuth = ref('visit')
      const authOptions = map2Options(COMMON_AUTH_OPTION_TYPE)
      const onSearchTeam = _.debounce((query) => {
        if (isEmpty(query)) {
          return
        }
        loading.value = true
        proxy.$api.post('/sys/resource/unreled/team/list', {
          rscId, teamNm: query
        }).then(res => {
          teamOptions.value = res.data || []
          loading.value = false
        }).catch(err => {
          console.error(err)
          loading.value = false
        })
      }, 500)
      const ok = () => {
        if (selectedTeams.value.length === 0) {
          return
        }
        let teamMembs = []
        selectedTeams.value.forEach(teamId => {
          teamMembs.push({
            teamId,
            rscId,
            rscTyp,
            teamAuth: selectedAuth.value
          })
        })
        return teamMembs
      }
      return {
        loading, selectedTeams, teamOptions, authOptions, selectedAuth,
        onSearchTeam, ok
      }
    }
  })
</script>
