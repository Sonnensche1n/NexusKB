<style lang="less">
.kb-team-invite {
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
  <div class="kb-team-invite">
    <n-select
      v-model:value="selectedMembs"
      multiple
      filterable
      placeholder="输入用户名称搜索"
      label-field="nkNm"
      value-field="userId"
      :options="userOptions"
      :loading="loading"
      clearable
      remote
      :clear-filter-after-select="true"
      @search="onSearchUser"
    />
    <n-select v-model:value="selectedRole" :options="roleOptions" style="width: 120px;" />
  </div>
</template>
<script>
  import { defineComponent, ref, reactive, getCurrentInstance, h } from 'vue'
  import { NTag, NBadge, useDialog } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate } from '@/libs/utils'
  import { isEmpty } from '@/libs/tools'
  import { AUTH_TEAM_ROLE_TYPE } from '@/libs/enum'
  import _ from 'lodash'
  export default defineComponent({
    components: {
    },
    props: {
      teamId: {
        type: String,
        required: true
      }
    },
    setup(props) {
      const { proxy, ctx } = getCurrentInstance()
      const teamId = props.teamId
      const dialog = useDialog()
      const loading = ref(false)
      const userOptions = ref([])
      const selectedMembs = ref([])
      const selectedRole = ref('member')
      const roleOptions = ref([])
      Object.keys(AUTH_TEAM_ROLE_TYPE).map(key => {
        if (key === 'creator') {
          return
        }
        roleOptions.value.push({
          label: AUTH_TEAM_ROLE_TYPE[key],
          value: key
        })
      })
      const onSearchUser = _.debounce((query) => {
        if (isEmpty(query)) {
          return
        }
        loading.value = true
        proxy.$api.post('/sys/team/uninvited/user/list', {
          teamId, nkNm: query
        }).then(res => {
          userOptions.value = res.data || []
          loading.value = false
        }).catch(err => {
          console.error(err)
          loading.value = false
        })
      }, 500)
      const ok = () => {
        if (selectedMembs.value.length === 0) {
          return
        }
        let teamMembs = []
        selectedMembs.value.forEach(userId => {
          teamMembs.push({
            userId: userId,
            teamId: props.teamId,
            teamRole: selectedRole.value
          })
        })
        return teamMembs
      }
      return {
        loading, selectedMembs, userOptions, roleOptions, selectedRole,
        onSearchUser, ok
      }
    }
  })
</script>
