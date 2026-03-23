<style lang="less">
.kb-team {
  height: 100%;
  .n-layout-sider {
    background-color: initial;
  }
  &-option {
    display: flex;
    justify-content: center;
  }
  &-list.n-list {
    margin-top: 20px;
    background-color: initial;
    .n-list-item {
      position: relative;
      padding: 10px;
      margin-bottom: 6px;
      cursor: pointer;
      .n-list-item__main {
        width: calc(100% - 26px);
        .n-thing, .n-thing-main {
          width: 100%;
          .n-icon {
            margin-right: 4px;
            position: relative;
            top: 1px;
          }
        }
      }
      .n-list-item__suffix {
        visibility: hidden;
      }
      &:hover {
        .n-list-item__suffix {
          visibility: visible;
          margin-left: 0;
        }
        &::before {
          content: '';
          width: 100%;
          height: 100%;
          position: absolute;
          left: 0;
          top: -1px;
          border-radius: var(--border-radius);
          background-color: var(--border-color);
          opacity: 0.1;
        }
      }
    }
    .selected.n-list-item {
      .n-thing-main__content {
        color: var(--primary-color);
      }
      &::before {
        content: '';
        width: 100%;
        height: 100%;
        position: absolute;
        left: 0;
        top: -1px;
        border-radius: var(--border-radius);
        background-color: var(--primary-color);
        opacity: 0.1;
      }
    }
  }
}
.kb-team.n-card>.n-card__content>.n-layout {
  height: 100%;
}
.kb-team.n-card>.n-card__content {
  padding: 0;
}
</style>

<template>
  <n-layout class="kb-team" has-sider>
    <n-layout-sider width="180px">
      <div class="kb-team-option">
        <n-button round @click="addTeam">
          <template #icon>
            <n-icon class="iconfont icon-plus"></n-icon>
          </template>
          新团队
        </n-button>
      </div>
      <n-list class="kb-team-list" :show-divider="false">
        <n-list-item v-for="team in teamList" :key="team.teamId" @click="onTeamSelect(team.teamId, team)" :class="selectedTeamId === team.teamId ? 'selected' : ''">
          <template #suffix v-if="team.teamRole === 'creator' || team.teamRole === 'manager'">
            <n-dropdown :options="teamOptions" :on-select="(key) => {
              this.onTeamOptionSelect(key, team)
            }">
              <n-button size="tiny"><n-icon class="iconfont icon-dotshorizontal"></n-icon></n-button>
            </n-dropdown>
          </template>
          <n-thing>
            <n-ellipsis>
              <n-icon class="iconfont-kb icon-team"></n-icon>{{ team.teamNm }}
            </n-ellipsis>
          </n-thing>
        </n-list-item>
      </n-list>
      <n-empty v-if="teamList.length === 0"/>
    </n-layout-sider>
    <n-layout-content>
      <team-memb :teamId="selectedTeamId" :team="selectedTeam" :key="selectedTeamId" v-if="selectedTeamId" />
    </n-layout-content>
  </n-layout>
</template>
<script>
  import { defineComponent, ref, getCurrentInstance, computed } from 'vue'
  import { useDialog } from 'naive-ui'
  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import TeamForm from './team/TeamForm.vue'
  import TeamMemb from './team/TeamMemb.vue'

  export default defineComponent({
    components: {
      TeamMemb
    },
    setup() {
      const dialog = useDialog()
      const { proxy, ctx } = getCurrentInstance()
      const teamList = ref([])
      const selectedTeamId = ref('')
      const selectedTeam = ref({})
      const initTeamList = () => {
        proxy.$api.post('/sys/team/my/list').then(res => {
          teamList.value = res.data || []
          if (teamList.value.length > 0) {
            selectedTeamId.value = teamList.value[0].teamId
            selectedTeam.value = teamList.value[0]
          } else {
            selectedTeamId.value = ''
            selectedTeam.value = {}
          }
        }).catch(err => {
          console.error(err)
        })
      }
      initTeamList()
      const teamOptions = [
        {
          label: '编辑',
          key: 'edit',
          icon: () => renderIconfontIcon('iconfont icon-pencil')
        },
        {
          label: '删除',
          key: 'delete',
          icon: () => renderIconfontIcon('iconfont icon-delete')
        }
      ]

      const onTeamSelect = (teamId, team) => {
        selectedTeamId.value = teamId
        selectedTeam.value = team
      }

      const addTeam = () => {
        dialogCreate(dialog, {
          title: `创建团队`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-team', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/sys/team', data).then(res => {
              teamList.value.unshift(res.data)
              selectedTeamId.value = res.data.teamId
              selectedTeam.value = res.data
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, TeamForm, {
        })
      }

      const editTeam = (team) => {
        dialogCreate(dialog, {
          title: `修改团队`,
          style: 'width: 40%;',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-team', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.put('/sys/team', data).then(res => {
              initTeamList()
              dialog.destroy()
            }).catch(err => {
              console.error(err)
              dialog.destroy()
            })
          }
        }, TeamForm, {
          team
        })
      }

      const onTeamOptionSelect = (key, team) => {
        if (key === 'edit') {
          editTeam(team)
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该团队么？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/sys/team/' + team.teamId).then(res => {
                initTeamList()
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
              return false
            }
          })
        }
      }

      return {
        selectedTeamId, selectedTeam, teamOptions, teamList,
        onTeamOptionSelect, onTeamSelect, addTeam
      }
    }
  })
</script>
